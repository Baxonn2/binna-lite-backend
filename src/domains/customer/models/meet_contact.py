from sqlmodel import SQLModel, Field

class MeetContact(SQLModel, table=True):
    meet_id: int = Field(foreign_key="meet.id", primary_key=True)
    contact_id: int = Field(foreign_key="contact.id", primary_key=True)