from datetime import datetime
from src.domains.openai_integration import Ignored, DateTimeString
from src.domains.customer.models.opportunity import Opportunity
from sqlmodel import Session, select
from typing import Optional

class OpportunityController:

    @staticmethod
    def create_opportunity(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: int,
        close_date: Optional[DateTimeString] = None,
        price: Optional[int] = None,
        notes: Optional[str] = None,
        product: Optional[str] = None,
    ) -> Opportunity:
        """
        Registra una nueva oportunidad de negocio en la base de datos del usuario. Para esto 
        se debe tener en cuenta el ID del cliente al que está relacionada la oportunidad.

        Args:
         - customer_id: ID del cliente al que está relacionada la oportunidad.
         - close_date: Fecha de cierre de la oportunidad. (Formato ISO 8601)
         - price: Valor monetario que se espera obtener de la oportunidad.
         - notes: Notas adicionales sobre la oportunidad.
         - product: Producto relacionado con la oportunidad.
        
        Returns:
         - Opportunity: La nueva oportunidad de negocio registrada.
        """
        parsed_close_date = datetime.fromisoformat(close_date) if close_date else None

        new_opportunity = Opportunity(
            close_date=parsed_close_date,
            price=price,
            notes=notes,
            user_id=user_id,
            customer_establishment_id=customer_id,
            product=product
        )

        db.add(new_opportunity)
        db.commit()
        db.refresh(new_opportunity)

        return new_opportunity
    

    @staticmethod
    def get_all_opportunities(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: Optional[int] = None
    ) -> list[Opportunity]:
        """
        Obtiene todas las oportunidades registradas por el usuario.

        Args:
         - customer_id: ID del cliente al que pertenecen las oportunidades.

        Returns:
         - list[Opportunity]: lista con todas las oportunidades registradas por el usuario.
        """
        query = select(Opportunity).where(Opportunity.user_id == user_id)
        if customer_id:
            query = query.where(Opportunity.customer_establishment_id == customer_id)

        return db.exec(query).all()
    
    
    @staticmethod
    def get_opportunity_by_id(
        db: Ignored[Session],
        user_id: Ignored[int],
        opportunity_id: int
    ) -> Opportunity:
        """
        Obtiene una oportunidad de negocio en específico.

        Args:
         - opportunity_id: ID de la oportunidad de negocio que se desea obtener.

        Returns:
         - Opportunity: La oportunidad de negocio solicitada.
        """
        query = select(Opportunity).where(
            Opportunity.id == opportunity_id,
            Opportunity.user_id == user_id
        )

        return db.exec(query).first()
    

    @staticmethod
    def update_opportunity(
        db: Ignored[Session],
        user_id: Ignored[int],
        opportunity_id: int,
        close_date: Optional[DateTimeString] = None,
        price: Optional[float] = None,
        notes: Optional[str] = None,
        stage: Optional[str] = None
    ) -> Opportunity:
        """
        Actualiza los datos de una oportunidad de negocio registrada por el usuario.

        Args:
         - opportunity_id: ID de la oportunidad de negocio que se va a actualizar.
         - close_date: Fecha de cierre de la oportunidad. (Formato ISO 8601)
         - price: Valor monetario que se espera obtener de la oportunidad.
         - notes: Notas adicionales sobre la oportunidad.
         - stage: Etapa en la que se encuentra la oportunidad (Pueden ser: "Prospección", "Calificación", "Propuesta técnica", "Negociación" o "Cierre").

        Returns:
         - Opportunity: La oportunidad de negocio actualizada.
        """
        opportunity = OpportunityController.get_opportunity_by_id(
            db, user_id, opportunity_id
        )

        if opportunity is None:
            return None

        if close_date is not None:
            opportunity.close_date = datetime.fromisoformat(close_date)
        if price is not None:
            opportunity.price = price
        if notes is not None:
            opportunity.notes = notes
        if stage is not None:
            opportunity.stage = stage

        db.commit()
        db.refresh(opportunity)

        return opportunity
    
    
    @staticmethod
    def delete_opportunity(
        db: Ignored[Session],
        user_id: Ignored[int],
        opportunity_id: int
    ) -> Opportunity:
        """
        Elimina una oportunidad de negocio registrada por el usuario.

        Args:
         - opportunity_id: ID de la oportunidad de negocio que se desea eliminar.

        Returns:
         - Opportunity: La oportunidad de negocio eliminada.
        """
        opportunity = OpportunityController.get_opportunity_by_id(
            db, user_id, opportunity_id
        )

        if opportunity is None:
            return None

        opportunity.deleted = True

        db.commit()
        db.refresh(opportunity)

        return opportunity