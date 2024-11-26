from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr

from src.domains.auth.models.user_session import UserSession

if TYPE_CHECKING:
    from src.domains.customer.models.establishment import CustomerEstablishment
    from src.domains.customer.models.contact import Contact
    from src.domains.customer.models.task import Task
    from src.domains.customer.models.opportunity import Opportunity
    from src.domains.customer.models.meet import Meet
    from src.domains.auth.models.user_usage import UserUsage
    from src.domains.auth.models.user_usage_limit import UserUsageLimit

class UserBase(SQLModel):
    username: str
    email: EmailStr
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None

    my_business_description: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    biography: Optional[str] = None

class UserRegister(UserBase):
    password: str
    password_confirmation: str

class User(UserBase, table = True):
    id: Optional[int] = Field(default= None, primary_key= True)

    hashed_password: str
    user_session: List[UserSession] = Relationship(back_populates= "user")

    establishments: List["CustomerEstablishment"] = Relationship(back_populates="user")
    contacts: List["Contact"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="user")
    opportunities: List["Opportunity"] = Relationship(back_populates="user")
    usages: List["UserUsage"] = Relationship(back_populates="user")
    usage_limits: List["UserUsageLimit"] = Relationship(back_populates="user")
    meets: List["Meet"] = Relationship(back_populates="user")

class UserInDB(UserBase):
    hashed_password: str

class UserResponse(UserBase):
    id: int