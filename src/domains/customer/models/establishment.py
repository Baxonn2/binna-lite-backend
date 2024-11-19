from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel
from src.utils.base_models import DeletableModel

from src.domains.auth.models.user import User

if TYPE_CHECKING:
    from src.domains.customer.models.additional_note import AdditionalNote
    from src.domains.customer.models.contact import Contact

class CustomerEstablishmentBase(SQLModel):
    name: str
    description: str
    industry: Optional[str] = None

class CustomerEstablishment(CustomerEstablishmentBase, DeletableModel, table=True):
    __tablename__ = "customer_establishment"

    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="establishments")

    additional_notes: list["AdditionalNote"] = Relationship(back_populates="customer_establishment")
    contacts: list["Contact"] = Relationship(back_populates="establishment")

class CustomerEstablishmentResponse(CustomerEstablishmentBase):
    id: int