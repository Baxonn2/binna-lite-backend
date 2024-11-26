from typing import Optional
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from src.utils.base_models import DeletableModel

from src.domains.auth.models.user import User
from src.domains.customer.models.contact import Contact
from src.domains.customer.models.establishment import CustomerEstablishment
from src.domains.customer.models.opportunity import Opportunity
from src.domains.customer.models.meet_contact import MeetContact

class MeetBase(SQLModel):
    name: str
    description: Optional[str]
    date: datetime
    duration_minutes: int
    status: str                 # pending, completed, cancelled
    address: Optional[str]

class Meet(MeetBase, DeletableModel, table=True):
    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="meets")

    customer_establishment_id: int = Field(foreign_key="customer_establishment.id")
    customer_establishment: CustomerEstablishment = Relationship(back_populates="meets")
    
    opportunity_id: Optional[int] = Field(foreign_key="opportunity.id")
    opportunity: Optional[Opportunity] = Relationship(back_populates="meets")

    contacts: list[Contact] = Relationship(back_populates="meets", link_model=MeetContact)
