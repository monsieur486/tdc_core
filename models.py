from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class LienCopainReunion(SQLModel, table=True):
    reunion_id: Optional[int] = Field(
        default=None, foreign_key="reunion.id", primary_key=True
    )
    copain_id: Optional[int] = Field(
        default=None, foreign_key="copain.id", primary_key=True
    )
    guest: bool = False
    dette_active: bool = False
    dette: float = 0.0

    reunion: "Reunion" = Relationship(back_populates="liens_copain")
    copain: "Copain" = Relationship(back_populates="liens_reunion")


class Reunion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    liens_copain: List[LienCopainReunion] = Relationship(back_populates="reunion")


class ReunionDetails(Reunion):
    guest: bool = False
    dette_active: bool = False
    dette: float = 0.0


class Copain(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    est_donneur: bool

    liens_reunion: List[LienCopainReunion] = Relationship(back_populates="copain")


class Contrat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    initiale: str
    points: int

