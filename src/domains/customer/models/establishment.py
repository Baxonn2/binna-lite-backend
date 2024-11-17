from typing import Optional

from sqlmodel import Field, Relationship, SQLModel
from src.utils.base_models import DeletableModel

from src.domains.auth.models.user import User

class CustomerEstablishmentBase(SQLModel):
    name: str
    description: str
    industry: Optional[str] = None

class CustomerEstablishment(CustomerEstablishmentBase, DeletableModel, table=True):
    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="establishments")

class CustomerEstablishmentResponse(CustomerEstablishmentBase):
    id: int