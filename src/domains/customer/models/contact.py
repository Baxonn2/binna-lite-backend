from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel
from src.utils.base_models import DeletableModel

from src.domains.auth.models.user import User
from src.domains.customer.models.establishment import CustomerEstablishment

class ContactBase(SQLModel):
    name: str
    role: str
    email: str
    phone: str

class Contact(ContactBase, DeletableModel, table=True):
    __tablename__ = "contact"

    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="contacts")

    establishment_id: int = Field(foreign_key="customer_establishment.id")
    establishment: "CustomerEstablishment" = Relationship(back_populates="contacts")