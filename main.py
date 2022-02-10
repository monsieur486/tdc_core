from fastapi import FastAPI, APIRouter
from sqlmodel import Session, SQLModel, create_engine, select

from fixtures.cagnottes_fixtures import cagnottes
from fixtures.contrats_fixtures import contrats
from fixtures.copains_fixtures import copains
from fixtures.liens_fixtures import liens
from fixtures.parties_fixtures import parties
from fixtures.reunions_fixtures import reunions
from models import Copain, Reunion, Default

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)
app = FastAPI()
reunion_router = APIRouter(tags=["Reunions"])
copain_router = APIRouter(tags=["Copains"])


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

        default_value = Default(cagnotte_id=2, reunion_id=3)
        session.add(default_value)
        session.commit()


@reunion_router.get("/reunions/")
def liste_reunions():
    with Session(engine) as session:
        reunions_db = session.exec(select(Reunion)).all()
        return reunions_db


@copain_router.get("/copain/")
def liste_copains():
    with Session(engine) as session:
        copains_db = session.exec(select(Copain)).all()
        return copains_db


app.include_router(reunion_router)
app.include_router(copain_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    fixtures()


@app.on_event("shutdown")
def on_startup():
    with Session(engine) as session:
        session.close()
        print("Bye")
