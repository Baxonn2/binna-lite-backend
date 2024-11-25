from sqlmodel import SQLModel, Field, Relationship

from src.utils.base_models import DeletableModel
from src.domains.auth.models.user_usage_limit import UserUsageLimit
from src.domains.auth.models.user import User

class UserUsageBase(SQLModel):
    total_tokens: int = Field(default=0)
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    cached_tokens: int = Field(default=0)


class UserUsage(UserUsageBase, DeletableModel, table=True):
    __tablename__ = "user_usage"

    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="usages")

    usage_limit_id: int = Field(foreign_key="user_usage_limit.id")
    usage_limit: UserUsageLimit = Relationship(back_populates="usages")

class UserUsageResponse(UserUsageBase):
    id: int
    user_id: int