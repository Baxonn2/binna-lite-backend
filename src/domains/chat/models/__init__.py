from sqlmodel import SQLModel
from typing import Optional

class MessageCreate(SQLModel):
    content: str
    thread_id: Optional[str]