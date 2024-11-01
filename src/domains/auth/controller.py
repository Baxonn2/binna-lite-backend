from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.utils.settings import AUTH_SECRET_KEY, AUTH_TOKEN_ALGORITHM
from src.domains.auth.models.user import User
from src.domains.auth.models.user_session import UserSession
from src.database.database import Database

database = Database()


def verify_password(plain_password, hashed_password):
        return CryptContext(schemes=["bcrypt"], deprecated="auto").verify(plain_password, hashed_password)
    
def get_password_hash(password):
    return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)
    
def get_user(db: Session, username: str) -> User | None:
    user = db.exec(select(User).filter(User.username == username)).first()
    if user is not None:
        return user
        
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=AUTH_TOKEN_ALGORITHM)
    return encoded_jwt
    
async def get_current_session(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="token"))],
    db: Session = Depends(database.get_db_session)
):
    try:
        jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_TOKEN_ALGORITHM])
        session = db.exec(
            select(UserSession).filter(
                UserSession.token == token
            )
        ).first()
        
        if session is None:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        if session.expiration < datetime.now():
            raise HTTPException(status_code=401, detail="Session has expired")
        
        if session.deleted is True:
            raise HTTPException(status_code=401, detail="Session has been deleted")
        
        return session
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(
    session: Annotated[UserSession, Depends(get_current_session)],
):
    user = session.user
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
    
    
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user
    
async def get_current_admin_user(
    active_user: Annotated[User, Depends(get_current_active_user)],
):
    if active_user.is_admin is not True:
        raise HTTPException(status_code=403, detail="No access permission")
    return active_user

def verify_access_token(self, token: str):
    try: 
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_TOKEN_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def save_user_session(db: Session, user_session: UserSession):
    on_db_user_session = db.exec(select(UserSession). filter(UserSession.id == user_session.id)).first()
    if on_db_user_session is not None:
        user_session.id == on_db_user_session.id
        db.merge(user_session)
        db.commit()
    else:
        db.add(user_session)
        db.commit()
        db.refresh(user_session)
    return user_session          
    
    