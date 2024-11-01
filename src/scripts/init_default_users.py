users = [
    {
        "username": "bot",
        "email": "bot@binna.app",
        "password": "superpass123132",
        "is_admin": True,
        "disabled": False
    }
]

from sqlmodel import Session, select
from src.database.database import Database
from src.domains.auth.models.user import User
from src.domains.auth.controller import get_password_hash

def save_users(db: Session):
    for user in users:
        user["hashed_password"] = get_password_hash(user["password"])

        user_on_db = db.exec(select(User).filter(User.username == user["username"])).first()
        if user_on_db:
            continue

        db.add(User(**user))
        db.commit()

db_generator = Database()
db_session = next(db_generator.get_db_session())

save_users(db_session)