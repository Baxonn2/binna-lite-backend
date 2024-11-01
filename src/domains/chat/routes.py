from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session
from fastapi.responses import StreamingResponse
from src.domains.auth.controller import get_current_active_user
from src.domains.auth.models.user import User
from src.database.database import Database
import src.domains.chat.controller as chat_controller
from src.domains.chat.models import MessageCreate

router = APIRouter(prefix="/chat",)
database = Database()

@router.post("/send")
def send_message(
    message: MessageCreate,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(database.get_db_session)
):
    return StreamingResponse(chat_controller.send_message(db, message, user))

@router.post("/create")
def create(
    user: User = Depends(get_current_active_user),
    db: Session = Depends(database.get_db_session)
):
    return {
        "thread_id": chat_controller.create_thread(db, user)
    }

@router.get("/retrieve")
def retrieve_messages(
    thread_id: Annotated[str, "The ID of the thread"],
    user: User = Depends(get_current_active_user),
    db: Session = Depends(database.get_db_session)
):
    return chat_controller.retrieve_messages(db, thread_id, user)