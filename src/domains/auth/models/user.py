from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr

from src.domains.auth.models.user_session import UserSession

class UserBase(SQLModel):
    username: str
    email: EmailStr
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserRegister(UserBase):
    password: str
    password_confirmation: str

class User(UserBase, table = True):
    id: Optional[int] = Field(default= None, primary_key= True)

    hashed_password: str
    user_session: List[UserSession] = Relationship(back_populates= "user")

class UserInDB(UserBase):
    hashed_password: str

class UserResponse(UserBase):
    id: int