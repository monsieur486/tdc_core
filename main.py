from fastapi import FastAPI, APIRouter
from sqlmodel import Session, SQLModel, create_engine, select
from models import Copain, Reunion

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)
app = FastAPI()
reunion_router = APIRouter(tags=["Reunions"])
copain_router = APIRouter(tags=["Copains"])


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@reunion_router.get("/reunions/")
def liste_reunions():
    with Session(engine) as session:
        reunions = session.exec(select(Reunion)).all()
        return reunions


@copain_router.get("/copain/")
def liste_copains():
    with Session(engine) as session:
        copains = session.exec(select(Copain)).all()
        return copains


app.include_router(reunion_router)
app.include_router(copain_router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
