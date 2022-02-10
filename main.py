from fastapi import FastAPI, APIRouter
from sqlmodel import Session, SQLModel, create_engine, select
from models import Copain, Reunion, Contrat, Cagnotte, LienCopainReunion, Partie

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
        copains = [
            Copain(nom="Laurent", est_donneur=True),
            Copain(nom="Dan", est_donneur=False),
            Copain(nom="Etienne", est_donneur=False),
            Copain(nom="JP", est_donneur=False),
            Copain(nom="Bernard", est_donneur=False),
        ]
        session.add_all(copains)

        contrats = [
            Contrat(nom="Petite", initiale="P", points=20),
            Contrat(nom="Garde", initiale="G", points=50),
            Contrat(nom="Garde-Sans", initiale="GS", points=100),
            Contrat(nom="Garde-Contre", initiale="GC", points=200),
            Contrat(nom="Chelem", initiale="C", points=500),
            Contrat(nom="Belge", initiale="B", points=0),
        ]
        session.add_all(contrats)

        cagnottes = [Cagnotte(nom="2021 TDC"), Cagnotte(nom="2022 TDC")]
        session.add_all(cagnottes)

        reunions = [
            Reunion(nom="2021-01-01", cagnotte_id=1),
            Reunion(nom="2021-01-02", cagnotte_id=1),
            Reunion(nom="2022-01-01", cagnotte_id=2),
        ]
        session.add_all(reunions)

        liens = [
            LienCopainReunion(
                reunion_id=1, copain_id=1, est_guest=False, dette_active=False, dette=0
            ),
            LienCopainReunion(
                reunion_id=1, copain_id=2, est_guest=False, dette_active=True, dette=1
            ),
            LienCopainReunion(
                reunion_id=1, copain_id=3, est_guest=False, dette_active=False, dette=0
            ),
            LienCopainReunion(
                reunion_id=1, copain_id=4, est_guest=False, dette_active=False, dette=0
            ),
            LienCopainReunion(
                reunion_id=1, copain_id=5, est_guest=True, dette_active=False, dette=0
            ),
            LienCopainReunion(
                reunion_id=2, copain_id=1, est_guest=False, dette_active=False, dette=1
            ),
            LienCopainReunion(
                reunion_id=2, copain_id=2, est_guest=False, dette_active=False, dette=2
            ),
            LienCopainReunion(
                reunion_id=2, copain_id=3, est_guest=False, dette_active=False, dette=0
            ),
            LienCopainReunion(
                reunion_id=2, copain_id=4, est_guest=False, dette_active=False, dette=0
            ),
            LienCopainReunion(
                reunion_id=3,
                copain_id=1,
                est_guest=False,
                dette_active=False,
                dette=0.5,
            ),
            LienCopainReunion(
                reunion_id=3,
                copain_id=2,
                est_guest=False,
                dette_active=False,
                dette=2.5,
            ),
            LienCopainReunion(
                reunion_id=3, copain_id=3, est_guest=False, dette_active=False, dette=0
            ),
            LienCopainReunion(
                reunion_id=3, copain_id=4, est_guest=False, dette_active=False, dette=0
            ),
            LienCopainReunion(
                reunion_id=3, copain_id=5, est_guest=True, dette_active=False, dette=0
            ),
        ]
        session.add_all(liens)

        parties = [
            Partie(
                reunion_id=1,
                contrat_id=1,
                preneur_id=1,
                appel_id=2,
                est_fait=True,
                points=10,
                chelem_realise=False,
                petit_au_bout=None
            ),
            Partie(
                reunion_id=1,
                contrat_id=2,
                preneur_id=1,
                appel_id=1,
                est_fait=False,
                points=0,
                chelem_realise=False,
                petit_au_bout=3
            ),
            Partie(
                reunion_id=1,
                contrat_id=2,
                preneur_id=3,
                appel_id=2,
                est_fait=True,
                points=0,
                chelem_realise=False,
                petit_au_bout=2
            ),
            Partie(
                reunion_id=1,
                contrat_id=3,
                preneur_id=3,
                appel_id=1,
                est_fait=True,
                points=40,
                chelem_realise=True,
                petit_au_bout=2
            )
        ]
        session.add_all(parties)

        session.commit()


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
    fixtures()
