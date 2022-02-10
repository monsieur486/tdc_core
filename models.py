from typing import Optional, List
from pydantic import condecimal
from sqlmodel import SQLModel, Field, Relationship


class Cagnotte(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)


class Contrat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    initiale: str
    points: int


class LienCopainReunion(SQLModel, table=True):
    reunion_id: Optional[int] = Field(
        default=None, foreign_key="reunion.id", primary_key=True
    )
    copain_id: Optional[int] = Field(
        default=None, foreign_key="copain.id", primary_key=True
    )
    est_guest: bool = Field(default=False)
    dette_active: bool = Field(default=False)
    dette: condecimal(max_digits=5, decimal_places=3) = Field(default=0)

    reunions: "Reunion" = Relationship(back_populates="liens_copains")
    copains: "Copain" = Relationship(back_populates="liens_reunions")


class Reunion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    cagnotte_id: Optional[int] = Field(default=None, foreign_key="cagnotte.id")
    liens_copains: List[LienCopainReunion] = Relationship(back_populates="reunions")


class ReunionDetails(Reunion):
    guest: bool = False
    dette_active: bool = False
    dette: float = 0.0


class Copain(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    est_donneur: bool = Field(default=False)

    liens_reunions: List[LienCopainReunion] = Relationship(back_populates="copains")


