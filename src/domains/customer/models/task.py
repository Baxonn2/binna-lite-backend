from typing import Optional
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from src.utils.base_models import DeletableModel

from src.domains.auth.models.user import User
from src.domains.customer.models.establishment import CustomerEstablishment


class TaskBase(SQLModel):
    name: str
    description: str
    due_date: Optional[datetime] = None
    completed: Optional[bool] = False

class Task(TaskBase, DeletableModel, table=True):
    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="tasks")

    establishment_id: int = Field(foreign_key="customer_establishment.id")
    establishment: CustomerEstablishment = Relationship(back_populates="tasks")