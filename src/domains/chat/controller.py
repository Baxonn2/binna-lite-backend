from sqlmodel import Session
from src.domains.auth.models.user import User
from src.domains.chat.models import MessageCreate
from src.domains.openai_integration.thread_manager import ThreadManager
from src.domains.auth.controllers.user_usage_controller import (
    UserUsageController, UserTokenLimitIsReachedException
)

def send_message(db: Session, message: MessageCreate, user: User):
    user_usage_limit = UserUsageController.get_active_usage_limit(db, user.id)

    if not user_usage_limit.can_use_more_tokens:
        raise UserTokenLimitIsReachedException

    return ThreadManager(
        message.thread_id, db, user
    ).stream_response(message.content)

def create_thread(db: Session, user: User):
    return ThreadManager(None, db, user).thread.id

def retrieve_messages(db: Session, thread_id: str, user: User):
    return ThreadManager(thread_id, db, user).retrieve_messages()