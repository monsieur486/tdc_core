from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Default(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reunion_id: Optional[int] = Field(default=None, foreign_key="reunion.id")


class Cagnotte(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    est_favori: bool = Field(default=True)


class CagnotteCreation(SQLModel):
    nom: str
    est_favori: bool


class Contrat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    initiale: str
    points: int


class Joueur(SQLModel, table=True):
    reunion_id: Optional[int] = Field(
        default=None, foreign_key="reunion.id", primary_key=True
    )
    copain_id: Optional[int] = Field(
        default=None, foreign_key="copain.id", primary_key=True
    )
    est_guest: bool = Field(default=False)
    dette_active: bool = Field(default=False)
    dette: int = Field(default=0)

    reunions: "Reunion" = Relationship(back_populates="liens_copains")
    copains: "Copain" = Relationship(back_populates="liens_reunions")


class JoueurAjout(SQLModel):
    copain_id: int
    est_guest: bool


class Reunion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    cagnotte_id: int = Field(default=None, foreign_key="cagnotte.id")
    liens_copains: List[Joueur] = Relationship(back_populates="reunions")


class ReunionCreation(SQLModel):
    nom: str


class Copain(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str = Field(index=True)
    image: Optional[str] = Field(default=None)

    liens_reunions: List[Joueur] = Relationship(back_populates="copains")


class CopainCreation(SQLModel):
    nom: str
    image: str


class Partie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reunion_id: int = Field(default=None, foreign_key="reunion.id")
    contrat_id: int = Field(default=None, foreign_key="contrat.id")
    preneur_id: int = Field(default=None, foreign_key="copain.id")
    appel_id: Optional[int] = Field(default=None, foreign_key="copain.id")
    est_fait: bool = Field(default=True)
    points: int = Field(default=0)
    chelem_realise: bool = Field(default=False)
    petit_au_bout: Optional[int] = Field(default=None, foreign_key="copain.id")


class PartieCreation(SQLModel):
    contrat_id: int
    preneur_id: int
    appel_id: Optional[int]
    est_fait: bool
    points: int
    chelem_realise: bool
    petit_au_bout: Optional[int]

