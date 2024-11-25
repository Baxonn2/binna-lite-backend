from typing import Annotated
from sqlmodel import Session
from fastapi import APIRouter, Depends

from src.database.database import Database
from src.domains.auth.models.user import User
from src.domains.auth.controller import get_current_active_user

router = APIRouter(prefix="/customer",)
database = Database()

from src.domains.customer.controllers.establishment_controller import EstablishmentController
from src.domains.customer.controllers.contact_controller import ContactController
from src.domains.customer.controllers.opportunity_controller import OpportunityController

@router.get("/")
def get_all_establishments(
    db: Session = Depends(database.get_db_session),
    user: User = Annotated[User, Depends(get_current_active_user)]
):
    return EstablishmentController.get_all_customer(
        db=db, user_id=user.id
    )

@router.get("/{customer_id}/contacts")
def get_all_contacts(
    customer_id: int,
    db: Session = Depends(database.get_db_session),
    user: User = Annotated[User, Depends(get_current_active_user)]
):
    return ContactController.get_all_contacts(
        db=db, user_id=user.id, customer_id=customer_id
    )


@router.get("/opportunities")
def get_all_opportunities(
    db: Session = Depends(database.get_db_session),
    user: User = Annotated[User, Depends(get_current_active_user)]
):
    return OpportunityController.get_all_opportunities(
        db=db, user_id=user.id
    )