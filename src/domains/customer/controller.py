from typing import Optional
from fastapi import Request
from sqlmodel import Session, select
from src.domains.customer.models.establishment import CustomerEstablishment
from src.domains.openai_integration import Ignored

class EstablishmentController:

    @staticmethod
    def create_customer(
        db: Ignored[Session],
        user_id: Ignored[int],
        name: str,
        description: str,
        industry: str,
    ) -> CustomerEstablishment:
        """
        Registra un nuevo cliente en la base de datos del usuario.

        Args:
         - name: Nombre del cliente que se va a registrar.
         - description: Descripción detallada de la empresa.
         - industry: Industria a la que pertenece la empresa (Se puede interpretar de la descripción del cliente).

        Returns:
         - CustomerEstablishment: El nuevo cliente registrado.
        """
        new_customer = CustomerEstablishment(
            name=name,
            description=description,
            industry=industry,
            user_id=user_id
        )

        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        return new_customer
    
    def get_all_customer(
        db: Ignored[Session],
        user_id: Ignored[int]
    ) -> list[CustomerEstablishment]:
        """
        Obtiene todos los clientes registrador por el usuario.

        Returns:
         - list[CustomerEstablishment]: lista con todos los clientes registrados por el usuario.
        """
        query = select(CustomerEstablishment).where(
            CustomerEstablishment.user_id == user_id
        )

        return db.exec(query).all()