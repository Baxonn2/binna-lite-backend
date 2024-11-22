from typing import Optional
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from src.utils.base_models import DeletableModel

from src.domains.auth.models.user import User
from src.domains.customer.models.contact import Contact
from src.domains.customer.models.establishment import CustomerEstablishment
from src.domains.customer.models.opportunity import Opportunity

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

    contact_id: int = Field(foreign_key="contact.id")
    contact: Contact = Relationship(back_populates="meets")
    