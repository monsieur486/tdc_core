from fastapi import FastAPI, APIRouter, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from fixtures.cagnottes_fixtures import cagnottes
from fixtures.contrats_fixtures import contrats
from fixtures.copains_fixtures import copains
from fixtures.liens_fixtures import liens
from fixtures.parties_fixtures import parties
from fixtures.reunions_fixtures import reunions
from models import Copain, Reunion, Default, Cagnotte, Contrat, CopainCreation, CagnotteCreation, ReunionCreation

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)
app = FastAPI()
reunion_router = APIRouter(tags=["Reunions"])
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


@reunion_router.get("/active/")
def reunion_active():
    with Session(engine) as session:
        default = session.get(Default, 1)
        if not default:
            raise HTTPException(status_code=404, detail="Pas de défault définis.")
        reunion_db = session.get(Reunion, default.reunion_id)
        if not reunion_db:
            raise HTTPException(status_code=404, detail="Pas de réunion par défault définie.")
        cagnotte = session.get(Cagnotte, reunion_db.cagnotte_id)
        if not cagnotte:
            raise HTTPException(status_code=404, detail="Pas de cagnotte par défault définie.")
        payload = {
            "id": reunion_db.id,
            "nom": reunion_db.nom,
            "cagnotte": cagnotte.nom
        }
        return payload


@reunion_router.post("/active/{reunion_id}")
def definir_reunion_active(reunion_id: int):
    with Session(engine) as session:
        default_db = session.get(Default, 1)
        if not default_db:
            raise HTTPException(status_code=404, detail="Pas de paramètres par défault définis.")
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
        reunions_db = session.exec(select(Reunion).where(Reunion.cagnotte_id == cagnotte_id).order_by(Reunion.nom.desc())).all()
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


@copain_router.patch("/copaines/{copain_id}")
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
        cagnottes_db = session.exec(select(Cagnotte).where(Cagnotte.est_favori).order_by(Cagnotte.nom.desc())).all()
        return cagnottes_db


@cagnotte_router.get("/cagnottes/archives/")
def liste_cagnottes_archivees():
    with Session(engine) as session:
        cagnottes_db = session.exec(
            select(Cagnotte).where(Cagnotte.est_favori == 0).order_by(Cagnotte.nom.desc())).all()
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


app.include_router(cagnotte_router)
app.include_router(reunion_router)
app.include_router(copain_router)
app.include_router(contrat_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    fixtures()


@app.on_event("shutdown")
def on_startup():
    with Session(engine) as session:
        session.close()
        print("Bye")
