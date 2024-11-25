from sqlmodel import Session, select
from typing import Optional
from src.domains.auth.models.user_usage import UserUsage
from src.domains.auth.models.user_usage_limit import UserUsageLimit
from datetime import datetime

class NotCurrentUsageLimitException(Exception):
    """
    This error is triggered when user has not an active UserUsageLimit.
    """
    pass

class UserTokenLimitIsReachedException(Exception):
    """
    This error is triggered when user has not tokens available.
    Is different to NotCurrentUsageLimitError, because in this case, user have a UserUsageLimit but
    the limit es reached.
    """
    pass

class UserUsageController:

    @staticmethod
    def registry_usage(
        db: Session,
        user_id: int,
        total_tokens: Optional[int] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        cached_tokens: Optional[int] = None
    ):
        """
        Registra el uso de tokens de un usuario.

        Args:
         - user_id: ID del usuario que realizó el uso de tokens.
         - total_tokens: Total de tokens utilizados.
         - prompt_tokens: Tokens utilizados en prompts.
         - completion_tokens: Tokens utilizados en completions.
         - cached_tokens: Tokens utilizados en cache.
        """
        current_usage = UserUsageController.get_active_usage_limit(db, user_id)

        new_usage = UserUsage(
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            user_id=user_id,
            usage_limit_id=current_usage.id
        )

        db.add(new_usage)

        current_usage.current_total_tokens_usage += total_tokens
        current_usage.current_prompt_tokens_usage += prompt_tokens
        current_usage.current_completion_tokens_usage += completion_tokens
        current_usage.current_cached_tokens_usage += cached_tokens

        db.commit()
        db.refresh(new_usage)

        return new_usage
    
    @staticmethod
    def get_active_usage_limit(db: Session, user_id: int) -> Optional[UserUsageLimit]:
        """
        Obtiene el límite de uso activo de un usuario.

        Args:
         - user_id: ID del usuario a consultar.
        """
        now = datetime.now()
        usage = db.exec(select(UserUsageLimit).where(
            UserUsageLimit.user_id == user_id,
            UserUsageLimit.start_period_date <= now,
            UserUsageLimit.finish_period_date >= now
        )).first()

        if not usage:
            print(f"Not usage found for user {user_id}")
            raise NotCurrentUsageLimitException()

        return usage
    