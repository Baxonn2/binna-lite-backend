from typing import Annotated
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from src.database.database import Database
from src.domains.auth.controller import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    save_user_session,
    get_user,
    get_password_hash,
    get_current_session
)
from src.domains.auth.models.user_session import UserSession
from src.domains.auth.models.user import User, UserRegister, UserBase, UserResponse

router = APIRouter(prefix="/auth",)
database = Database()

@router.post("/login")
def login(
    request : Request,
    db: Session = Depends(database.get_db_session),
    form_data: OAuth2PasswordRequestForm = Depends()    
) -> UserSession:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expiration = datetime.now() + timedelta(minutes=10080)
    access_token_expires = timedelta(minutes=10080)
    client_host = request.client.host
    data_to_encrypt = {
        "sub": user.username,
        "is_admin": user.is_admin
    }
    access_token = create_access_token(
        data=data_to_encrypt, expires_delta=access_token_expires
    )
    user_session = UserSession(
        device=client_host,
        expiration=expiration,
        token=access_token,
        user_id=user.id
    )
    if user_session.deleted == True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User session deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return save_user_session(db, user_session)

@router.post("/logout")
def logout(
    current_session: Annotated[UserSession, Depends(get_current_session)],
    db: Session = Depends(database.get_db_session)
) -> None:
    session = db.get(UserSession, current_session.id)
    session.deleted = True  
    
    db.commit()
    return None

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@router.get("/session")
def get_user_session(
    current_session: Annotated[UserSession, Depends(get_current_session)],
) -> UserSession:
    return current_session

@router.post("/register", response_model=UserBase)
def register_user(
    user: UserRegister,
    db: Session = Depends(database.get_db_session)
    ) -> User:
    user_on_db = get_user(db, user.username)
    if user_on_db is not None:
        raise HTTPException(status_code= 401, detail= "Username already registered")
    if user.password != user.password_confirmation:
        raise HTTPException(status_code= 401, detail= "Passwords do not match")
    else:
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    return new_user