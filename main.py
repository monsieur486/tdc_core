import config
import uvicorn
from typing import List
from fastapi import Depends, FastAPI, HTTPException, Query, APIRouter
from sqlmodel import Session, select
from database import create_db_and_tables, get_session, engine
from models import (
    HeroRead,
    Hero,
    HeroReadWithTeam,
    HeroUpdate,
    TeamRead,
    Team,
    TeamCreate,
    TeamReadWithHeroes,
    TeamUpdate,
)

app = FastAPI()

team_router = APIRouter(tags=["Equipes"])
hero_router = APIRouter(tags=["Héros"])


def import_fixtures():
    with Session(engine) as session:
        team01 = Team(name="Equipe Une", headquarters="Coco")
        team02 = Team(name="Equipe Deux", headquarters="Roger")

        session.add(team01)
        session.add(team02)
        session.commit()

        hero01 = Hero(name="Emile", secret_name="007", team_id=team01.id)
        hero02 = Hero(name="Riton", secret_name="Gérard", team_id=team01.id)

        session.add(hero01)
        session.add(hero02)
        session.commit()


@app.on_event("startup")
def on_startup():
    with Session(engine) as session:
        session.execute("drop table if exists hero")
        session.execute("drop table if exists team")

    create_db_and_tables()
    import_fixtures()


@hero_router.post("/heroes/", response_model=HeroUpdate)
def create_hero(*, session: Session = Depends(get_session), hero: HeroUpdate):
    db_hero = Hero.from_orm(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@hero_router.get("/heroes/", response_model=List[HeroRead])
def read_heroes(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@hero_router.get("/heroes/{hero_id}", response_model=HeroReadWithTeam)
def read_hero(*, session: Session = Depends(get_session), hero_id: int):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@hero_router.patch("/heroes/{hero_id}", response_model=HeroRead)
def update_hero(
        *, session: Session = Depends(get_session), hero_id: int, hero: HeroUpdate
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.dict(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@hero_router.delete("/heroes/{hero_id}")
def delete_hero(*, session: Session = Depends(get_session), hero_id: int):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}


@team_router.post("/teams/", response_model=TeamRead)
def create_team(*, session: Session = Depends(get_session), team: TeamCreate):
    db_team = Team.from_orm(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_router.get("/teams/", response_model=List[TeamRead])
def read_teams(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    teams = session.exec(select(Team).offset(offset).limit(limit)).all()
    return teams


@team_router.get("/teams/{team_id}", response_model=TeamReadWithHeroes)
def read_team(*, team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@team_router.patch("/teams/{team_id}", response_model=TeamRead)
def update_team(
        *,
        session: Session = Depends(get_session),
        team_id: int,
        team: TeamUpdate,
):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.dict(exclude_unset=True)
    for key, value in team_data.items():
        setattr(db_team, key, value)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_router.delete("/teams/{team_id}")
def delete_team(*, session: Session = Depends(get_session), team_id: int):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"ok": True}


app.include_router(team_router)
app.include_router(hero_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        log_level=config.log_level,
        reload=config.reload,
    )
