from typing import Optional
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from src.utils.base_models import DeletableModel

from src.domains.customer.models.establishment import CustomerEstablishment
from src.domains.auth.models.user import User


class OpportunityBase(SQLModel):
    product: Optional[str] = None
    close_date: Optional[datetime] = None
    price: Optional[float] = None
    stage: Optional[str] = None
    notes: Optional[str] = None

class Opportunity(OpportunityBase, DeletableModel, table=True):
    id: int = Field(default=None, primary_key=True)

    customer_establishment_id: int = Field(foreign_key="customer_establishment.id")
    customer_establishment: "CustomerEstablishment" = Relationship(back_populates="opportunities")

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="opportunities")