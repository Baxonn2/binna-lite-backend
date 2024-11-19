from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from src.utils.base_models import DeletableModel

from src.domains.customer.models.establishment import CustomerEstablishment


class AdditionalNoteBase(SQLModel):
    title: str
    content: str

class AdditionalNote(AdditionalNoteBase, DeletableModel, table=True):
    __tablename__ = "additional_note"

    id: int = Field(default=None, primary_key=True)

    customer_establishment_id: int = Field(foreign_key="customer_establishment.id")
    customer_establishment: "CustomerEstablishment" = Relationship(back_populates="additional_notes")

class AdditionalNoteResponse(AdditionalNoteBase):
    id: int

class AdditionalNoteSummarizedResponse(SQLModel):
    id: int
    title: str
    customer_establishment_id: int