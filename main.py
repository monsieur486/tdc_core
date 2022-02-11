from fastapi import FastAPI, APIRouter, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from fixtures.cagnottes_fixtures import cagnottes
from fixtures.contrats_fixtures import contrats
from fixtures.copains_fixtures import copains
from fixtures.liens_fixtures import liens
from fixtures.parties_fixtures import parties
from fixtures.reunions_fixtures import reunions
from models import Copain, Reunion, Default, Cagnotte, Contrat, CopainCreation, CagnotteCreation

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


@reunion_router.get("/reunions/")
def liste_reunions():
    with Session(engine) as session:
        reunions_db = session.exec(select(Reunion).order_by(Reunion.nom.desc())).all()
        return reunions_db


@reunion_router.get("/reunions/active/")
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
            "nom": reunion_db.nom,
            "cagnotte": cagnotte.nom
        }
        return payload


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


@cagnotte_router.get("/cagnottes/")
def liste_cagnottes():
    with Session(engine) as session:
        cagnottes_db = session.exec(select(Cagnotte)).all()
        return cagnottes_db


@cagnotte_router.post("/cagnottes/")
def creation_cagnotte(cagnotte: CagnotteCreation):
    with Session(engine) as session:
        cagnotte_db = Cagnotte.from_orm(cagnotte)
        session.add(cagnotte_db)
        session.commit()
        session.refresh(cagnotte_db)
        return cagnotte_db


@contrat_router.get("/contrats/")
def liste_contrats():
    with Session(engine) as session:
        contrats_db = session.exec(select(Contrat)).all()
        return contrats_db


app.include_router(reunion_router)
app.include_router(cagnotte_router)
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
