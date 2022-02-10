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
    dette: condecimal(max_digits=6, decimal_places=2) = Field(default=0)

    reunions: "Reunion" = Relationship(back_populates="liens_copains")
    copains: "Copain" = Relationship(back_populates="liens_reunions")


class Reunion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    cagnotte_id: int = Field(default=None, foreign_key="cagnotte.id")
    liens_copains: List[LienCopainReunion] = Relationship(back_populates="reunions")


class Copain(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    est_donneur: bool = Field(default=False)

    liens_reunions: List[LienCopainReunion] = Relationship(back_populates="copains")


class Partie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reunion_id: int = Field(default=None, foreign_key="reunion.id")
    contrat_id: int = Field(default=None, foreign_key="contrat.id")
    preneur_id: int = Field(default=None, foreign_key="copain.id")
    appel_id: Optional[int] = Field(default=None, foreign_key="copain.id")
    est_fait: bool
    points: int
    chelem_realise: bool
    petit_au_bout: Optional[int] = Field(default=None, foreign_key="copain.id")
