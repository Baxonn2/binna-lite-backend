from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from src.domains.auth.models.user import User
from src.utils.base_models import DeletableModel

if TYPE_CHECKING:
    from src.domains.auth.models.user_usage import UserUsage

class UserUsageLimitBase(SQLModel):
    max_total_tokens_usage: int = Field(default=0)
    is_unlimited_total_tokens_usage: bool = Field(default=False)

    current_total_tokens_usage: int = Field(default=0)
    current_prompt_tokens_usage: int = Field(default=0)
    current_completion_tokens_usage: int = Field(default=0)
    current_cached_tokens_usage: int = Field(default=0)

    start_period_date: str = Field(default=None)
    finish_period_date: str = Field(default=None)
    
    @property
    def is_current(self) -> bool:
        return self.start_period_date <= self.finish_period_date

    @property
    def is_unlimited(self) -> bool:
        return self.is_unlimited_total_tokens_usage
    
    @property
    def is_expired(self) -> bool:
        return self.finish_period_date < self.start_period_date
    
    @property
    def is_future(self) -> bool:
        return self.start_period_date > self.finish_period_date
    
    @property
    def can_use_more_tokens(self) -> bool:
        if not self.is_current:
            return False
        return self.current_total_tokens_usage < self.max_total_tokens_usage


class UserUsageLimit(UserUsageLimitBase, DeletableModel, table=True):
    __tablename__ = "user_usage_limit"

    id: int = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="usage_limits")

    usages: list["UserUsage"] = Relationship(back_populates="usage_limit")

    
class UserUsageLimitResponse(UserUsageLimitBase):
    id: int
    user_id: int
    usages: list["UserUsage"] = []