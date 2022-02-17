from operator import itemgetter

from fastapi import FastAPI, APIRouter, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from fixtures.cagnottes_fixtures import cagnottes
from fixtures.contrats_fixtures import contrats
from fixtures.copains_fixtures import copains
from fixtures.liens_fixtures import liens
from fixtures.parties_fixtures import parties
from fixtures.reunions_fixtures import reunions
from models import (
    Copain,
    Reunion,
    Default,
    Cagnotte,
    Contrat,
    CopainCreation,
    CagnotteCreation,
    ReunionCreation,
    Joueur,
    Partie, PartieCreation,
)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)
app = FastAPI()
reunion_router = APIRouter(tags=["Reunions"])
partie_router = APIRouter(tags=["Parties"])
cagnotte_router = APIRouter(tags=["Cagnottes"])
copain_router = APIRouter(tags=["Copains"])
contrat_router = APIRouter(tags=["Contrats"])


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def fixtures():
    with Session(engine) as session:
        session.add_all(copains)
        session.commit()
        session.add_all(contrats)
        session.commit()
        session.add_all(cagnottes)
        session.commit()
        session.add_all(reunions)
        session.commit()
        session.add_all(liens)
        session.commit()
        session.add_all(parties)
        session.commit()

        default_value = Default(reunion_id=3)
        session.add(default_value)
        session.commit()


def joueurs_par_reunion(reunion_id: int):
    with Session(engine) as session:
        joueurs = session.exec(
            select(Joueur).where(Joueur.reunion_id == reunion_id)
        ).all()
        if not joueurs:
            return []
        joueur_db = []
        nombre_joueurs = 0
        for joueur in joueurs:
            copain = session.get(Copain, joueur.copain_id)
            if not copain:
                raise HTTPException(
                    status_code=404, detail="Copain lié au joueur introuvable."
                )
            nombre_joueurs += 1
            dettes = session.exec(
                select(Joueur)
                .where(Joueur.dette_active)
                .where(Joueur.copain_id == joueur.copain_id)
            )
            dettes_result = []
            for dette in dettes:
                reunion = session.get(Reunion, dette.reunion_id)
                reunion_db = {
                    "reunion_id": reunion.id,
                    "nom": reunion.nom,
                    "dette": dette.dette,
                }
                if reunion.id != reunion_id:
                    dettes_result.append(reunion_db)

            payload = {
                "copain_id": joueur.copain_id,
                "copain_nom": copain.nom,
                "copain_image": copain.image,
                "est_guest": joueur.est_guest,
                "dette": joueur.dette,
                "dette_active": joueur.dette_active,
                "dettes": dettes_result,
            }
            joueur_db.append(payload)
            joueurs_tries = sorted(
                joueur_db, key=itemgetter("copain_nom"), reverse=False
            )

        return {"nombre_joueurs": nombre_joueurs, "joueurs": joueurs_tries}


def calcul_points(informations, parties_db):
    return {"inscrits": informations, "parties": parties_db}


@reunion_router.get("/active/")
def reunion_active():
    with Session(engine) as session:
        default = session.get(Default, 1)
        if not default:
            raise HTTPException(
                status_code=404, detail="Pas de réunion par défault définie."
            )
        reunion_db = session.get(Reunion, default.reunion_id)
        if not reunion_db:
            raise HTTPException(
                status_code=404, detail="Pas de réunion par défault définie."
            )
        cagnotte = session.get(Cagnotte, reunion_db.cagnotte_id)
        if not cagnotte:
            raise HTTPException(status_code=404, detail="Cagnotte introuvable.")
        informations = joueurs_par_reunion(reunion_db.id)
        nombre_joueurs = informations["nombre_joueurs"]
        joueurs = informations["joueurs"]
        parties_db = liste_parties_par_reunion(reunion_db.id)
        parties_result = []
        nombre_parties = 0
        for partie in parties_db:
            nombre_parties += 1
            partie_db = {
                "rang": nombre_parties,
                "contrat_id": partie.contrat_id,
                "preneur_id": partie.preneur_id,
                "appel_id": partie.appel_id,
                "est_fait": partie.est_fait,
                "points": partie.points,
                "chelem_realise": partie.chelem_realise,
                "petit_au_bout": partie.petit_au_bout,
            }
            parties_result.append(partie_db)

        contrats_db = session.exec(select(Contrat)).all()

        payload = {
            "reunion_id": reunion_db.id,
            "reunion_nom": reunion_db.nom,
            "cagnotte_id": cagnotte.id,
            "cagnotte_nom": cagnotte.nom,
            "nombre_joueurs": nombre_joueurs,
            "joueurs": joueurs,
            "nombre_parties": nombre_parties,
            "parties": parties_result,
            "contrats": contrats_db
        }
        return payload


@reunion_router.post("/active/{reunion_id}")
def definir_reunion_active(reunion_id: int):
    with Session(engine) as session:
        default_db = session.get(Default, 1)
        if not default_db:
            raise HTTPException(
                status_code=404, detail="Pas de paramètres par défault définis."
            )
        reunion = session.get(Reunion, reunion_id)
        if not reunion:
            raise HTTPException(status_code=404, detail="Réunion introuvable")
        default_db.reunion_id = reunion_id
        session.add(default_db)
        session.commit()
        session.refresh(default_db)
        return {"message": "Réunion activée"}


@reunion_router.get("/reunions/{cagnotte_id}")
def liste_reunions(cagnotte_id: int):
    with Session(engine) as session:
        cagnotte = session.get(Cagnotte, cagnotte_id)
        if not cagnotte:
            raise HTTPException(status_code=404, detail="Cagnotte introuvable")
        reunions_db = session.exec(
            select(Reunion)
            .where(Reunion.cagnotte_id == cagnotte_id)
            .order_by(Reunion.nom.desc())
        ).all()
        return reunions_db


@reunion_router.post("/reunions/{cagnotte_id}")
def ajout_reunion(cagnotte_id: int, reunion: ReunionCreation):
    with Session(engine) as session:
        cagnotte = session.get(Cagnotte, cagnotte_id)
        if not cagnotte:
            raise HTTPException(status_code=404, detail="Cagnotte introuvable")
        reunion_db = Reunion.from_orm(reunion)
        reunion_db.cagnotte_id = cagnotte.id
        session.add(reunion_db)
        session.commit()
        session.refresh(reunion_db)

        definir_reunion_active(reunion_db.id)

        return {"message": "Réunion créée"}


@reunion_router.post("/reunions/{reunion_id}/joueurs/{copain_id}")
def paiement_dette(reunion_id: int, copain_id: int):
    with Session(engine) as session:
        joueur = session.exec(
            select(Joueur)
            .where(Joueur.reunion_id == reunion_id)
            .where(Joueur.copain_id == copain_id)
        ).one_or_none()
        if not joueur:
            raise HTTPException(status_code=404, detail="Dette introuvable")
        joueur.dette_active = False
        session.add(joueur)
        session.commit()
        return {"message": "Dette payée"}


@copain_router.get("/copains/")
def liste_copains():
    with Session(engine) as session:
        copains_db = session.exec(select(Copain)).all()
        return copains_db


@copain_router.post("/copains/")
def creation_copain(copain: CopainCreation):
    with Session(engine) as session:
        copain_db = Copain.from_orm(copain)
        session.add(copain_db)
        session.commit()
        session.refresh(copain_db)
        return copain_db


@copain_router.patch("/copains/{copain_id}")
def mise_a_jour_copain(copain_id: int, copain: CopainCreation):
    with Session(engine) as session:
        db_copain = session.get(Copain, copain_id)
        if not db_copain:
            raise HTTPException(status_code=404, detail="Copain introuvable")
        copain_data = copain.dict(exclude_unset=True)
        for key, value in copain_data.items():
            setattr(db_copain, key, value)
        session.add(db_copain)
        session.commit()
        session.refresh(db_copain)
        return {"message": "Copain mis à jour"}


@cagnotte_router.get("/cagnottes/")
def liste_cagnottes():
    with Session(engine) as session:
        cagnottes_db = session.exec(
            select(Cagnotte).where(Cagnotte.est_favori).order_by(Cagnotte.nom.desc())
        ).all()
        return cagnottes_db


@cagnotte_router.get("/cagnottes/archives/")
def liste_cagnottes_archivees():
    with Session(engine) as session:
        cagnottes_db = session.exec(
            select(Cagnotte)
            .where(Cagnotte.est_favori == 0)
            .order_by(Cagnotte.nom.desc())
        ).all()
        return cagnottes_db


@cagnotte_router.post("/cagnottes/")
def creation_cagnotte(cagnotte: CagnotteCreation):
    with Session(engine) as session:
        cagnotte_db = Cagnotte.from_orm(cagnotte)
        session.add(cagnotte_db)
        session.commit()
        session.refresh(cagnotte_db)
        return cagnotte_db


@cagnotte_router.patch("/cagnottes/{cagnotte_id}")
def mise_a_jour_cagnotte(cagnotte_id: int, cagnotte: CagnotteCreation):
    with Session(engine) as session:
        db_cagnotte = session.get(Cagnotte, cagnotte_id)
        if not db_cagnotte:
            raise HTTPException(status_code=404, detail="Cagnotte introuvable")
        cagnotte_data = cagnotte.dict(exclude_unset=True)
        for key, value in cagnotte_data.items():
            setattr(db_cagnotte, key, value)
        session.add(db_cagnotte)
        session.commit()
        session.refresh(db_cagnotte)
        return {"message": "Cagnotte mise à jour"}


@cagnotte_router.post("/cagnottes/{cagnotte_id}/archive")
def archive_cagnotte(cagnotte_id: int):
    with Session(engine) as session:
        db_cagnotte = session.get(Cagnotte, cagnotte_id)
        if not db_cagnotte:
            raise HTTPException(status_code=404, detail="Cagnotte introuvable")
        db_cagnotte.est_favori = False
        session.add(db_cagnotte)
        session.commit()
        return {"message": "Cagnotte archivée"}


@cagnotte_router.post("/cagnottes/{cagnotte_id}/active")
def active_cagnotte(cagnotte_id: int):
    with Session(engine) as session:
        db_cagnotte = session.get(Cagnotte, cagnotte_id)
        if not db_cagnotte:
            raise HTTPException(status_code=404, detail="Cagnotte introuvable")
        db_cagnotte.est_favori = True
        session.add(db_cagnotte)
        session.commit()
        return {"message": "Cagnotte activée"}


@contrat_router.get("/contrats/")
def liste_contrats():
    with Session(engine) as session:
        contrats_db = session.exec(select(Contrat)).all()
        return contrats_db


@partie_router.get("/parties/{reunion_id}")
def liste_parties_par_reunion(reunion_id: int):
    with Session(engine) as session:
        parties_db = session.exec(
            select(Partie).where(Partie.reunion_id == reunion_id)
        ).all()
        return parties_db


@partie_router.post("/parties/{reunion_id}")
def ajout_partie(reunion_id: int, partie: PartieCreation):
    with Session(engine) as session:
        partie_db = Partie.from_orm(partie)
        partie_db.reunion_id = reunion_id
        session.add(partie_db)
        session.commit()
        session.refresh(partie_db)
        return {"message": "Partie ajoutée"}


app.include_router(copain_router)
app.include_router(cagnotte_router)
app.include_router(reunion_router)
app.include_router(partie_router)
app.include_router(contrat_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    fixtures()


@app.on_event("shutdown")
def on_startup():
    with Session(engine) as session:
        session.close()
        print("Ciao ciao")
