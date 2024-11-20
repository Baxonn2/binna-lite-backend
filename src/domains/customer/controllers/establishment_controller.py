from typing import Optional
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
         - CustomerEstablishment: El nuevo cliente registrado. Si ya existe un cliente con el mismo
           nombre se retornará el cliente existente.
        """
        existing_customer = EstablishmentController.get_customer_by_name(
            db, user_id, name, use_fuzzy_search=True
        )

        if existing_customer:
            return existing_customer

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
    

    @staticmethod
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
            CustomerEstablishment.user_id == user_id,
            CustomerEstablishment.deleted == False
        )

        return db.exec(query).all()
    
    @staticmethod
    def get_customer_by_id(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: int
    ) -> Optional[CustomerEstablishment]:
        """
        Obtiene un cliente registrado por el usuario.

        Args:
        - customer_id: Identificador del cliente que se va a buscar.

        Returns:
         - Optional[CustomerEstablishment]: Cliente registrado por el usuario.
        """
        query = select(CustomerEstablishment).where(
            CustomerEstablishment.user_id == user_id,
            CustomerEstablishment.id == customer_id
        )

        return db.exec(query).first()
    
    @staticmethod
    def update_customer(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Optional[CustomerEstablishment]:
        """
        Actualiza un cliente registrado por el usuario.

        Args:
        - name: Nombre del cliente que se va a registrar.
        - description: Descripción detallada de la empresa.
        - industry: Industria a la que pertenece la empresa (Se puede interpretar de la descripción del cliente).
        - customer_id: Identificador del cliente que se va a actualizar.

        Returns:
         - Optional[CustomerEstablishment]: Cliente actualizado.
        """
        customer = EstablishmentController.get_customer_by_id(db, user_id, customer_id)

        if customer is None:
            return None

        if name is not None:
            customer.name = name
        if description is not None:
            customer.description = description
        if industry is not None:
            customer.industry = industry

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer
    

    @staticmethod
    def delete_customer(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: int
    ) -> Optional[CustomerEstablishment]:
        """
        Elimina un cliente registrado por el usuario.

        Args:
        - customer_id: Identificador del cliente que se va a eliminar.

        Returns:
         - Optional[CustomerEstablishment]: Cliente eliminado.
        """
        customer = EstablishmentController.get_customer_by_id(db, user_id, customer_id)

        if customer is None:
            return None

        customer.deleted = True

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return customer
    

    @staticmethod
    def get_customer_by_name(
        db: Ignored[Session],
        user_id: Ignored[int],
        name: str,
        use_fuzzy_search: Optional[bool] = False
    ) -> Optional[CustomerEstablishment]:
        """
        Obtiene un cliente registrado por el usuario.

        Args:
        - name: Nombre del cliente que se va a buscar.
        - use_fuzzy_search: Si es verdadero, se buscará un cliente con un nombre similar al proporcionado.

        Returns:
         - Optional[CustomerEstablishment]: Cliente registrado por el usuario.
        """
        query = select(CustomerEstablishment).where(
            CustomerEstablishment.user_id == user_id,
            CustomerEstablishment.name == name
        )

        customer_matched = db.exec(query).first()

        if customer_matched or not use_fuzzy_search:
            return customer_matched
        
        # If not found, try to find a customer with a similar name
        query = select(CustomerEstablishment).where(
            CustomerEstablishment.user_id == user_id,
        )
    
        customers = db.exec(query).all()

        for customer in customers:
            if name.lower() in customer.name.lower():
                return customer
        
        return None