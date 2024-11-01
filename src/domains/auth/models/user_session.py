from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

if TYPE_CHECKING:
    from src.domains.auth.models.user import User
    
class UserSessionBase(SQLModel):
    created_at: datetime = Field(
        default_factory= lambda: datetime.now(),
    )
    device: str
    expiration: datetime
    token: str
    deleted: Optional[bool] = None
    user_id: int = Field(foreign_key="user.id")

class UserSession(UserSessionBase, table = True):
    id: Optional[int] = Field(default= None, primary_key= True)

    user: "User" = Relationship(back_populates= "user_session")

class UserSessionData(UserSessionBase):
    id: Optional[int] = None

