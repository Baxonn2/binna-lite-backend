from sqlmodel import Session, select
from typing import Optional
from datetime import datetime

from src.domains.openai_integration import Ignored, DateTimeString
from src.domains.customer.models.meet import Meet
from src.domains.customer.models.meet_contact import MeetContact


class MeetController:

    @staticmethod
    def create_meet(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: int,
        name: str,
        date: DateTimeString,
        duration_minutes: int,
        status: str,
        description: Optional[str] = None,
        address: Optional[str] = None,
        opportunity_id: Optional[int] = None,
        contact_ids: Optional[str] = None
    ):
        """
        Registra una nueva reunión en la base de datos del usuario.

        Args:
         - customer_id: ID del cliente al que está relacionada la reunión.
         - name: Nombre de la reunión que se va a registrar.
         - date: Fecha y hora de la reunión.
         - duration_minutes: Duración de la reunión en minutos.
         - status: Estado actual de la reunión. (pending, completed, cancelled)
         - description: Descripción detallada de la reunión.
         - address: Dirección donde se llevará a cabo la reunión.
         - opportunity_id: ID de la oportunidad relacionada con la reunión.
         - contact_ids: IDs de los contactos relacionados con la reunión. (Si son varios, se separan por comas)
         
        Returns:
         - Meet: La nueva reunión registrada.
        """
        parsed_date = datetime.fromisoformat(date)

        new_meet = Meet(
            name=name,
            description=description,
            date=parsed_date,
            duration_minutes=duration_minutes,
            status=status,
            address=address,
            user_id=user_id,
            customer_establishment_id=customer_id,
            opportunity_id=opportunity_id
        )

        if contact_ids:
            for contact_id in contact_ids.split(','):
                new_meet_contact = MeetContact(
                    meet_id=new_meet.id,
                    contact_id=int(contact_id)
                )
                db.add(new_meet_contact)

        db.add(new_meet)
        db.commit()
        db.refresh(new_meet)

        return new_meet
    

    @staticmethod
    def get_all_meets(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: Optional[int] = None,
        from_date_filter: Optional[DateTimeString] = None,
        to_date_filter: Optional[DateTimeString] = None,
    ) -> list[Meet]:
        """
        Obtiene todas las reuniones registradas por el usuario.

        Args:
         - customer_id: ID del cliente al que están relacionadas las reuniones.
         - from_date_filter: Fecha y hora de inicio del rango de fechas de las reuniones a obtener.
         - to_date_filter: Fecha y hora de fin del rango de fechas de las reuniones a obtener.

        Returns:
         - list[Meet]: lista con todas las reuniones registradas por el usuario.
        """
        query = select(Meet).where(
            Meet.user_id == user_id
        )

        if customer_id:
            query = query.where(Meet.customer_establishment_id == customer_id)

        if from_date_filter:
            parsed_from_date = datetime.fromisoformat(from_date_filter)
            query = query.where(Meet.date >= parsed_from_date)
        
        if to_date_filter:
            parsed_to_date = datetime.fromisoformat(to_date_filter)
            query = query.where(Meet.date <= parsed_to_date)

        meets = db.exec(query).all()
        return meets
    

    @staticmethod
    def get_meet(
        db: Ignored[Session],
        user_id: Ignored[int],
        meet_id: int
    ) -> Meet:
        """
        Obtiene la información de una reunión específica.

        Args:
         - meet_id: ID de la reunión que se desea obtener.

        Returns:
         - Meet: La reunión solicitada.
        """
        query = select(Meet).where(
            Meet.id == meet_id,
            Meet.user_id == user_id
        )
        meet = db.exec(query).first()
        return meet
    

    @staticmethod
    def update_meet(
        db: Ignored[Session],
        user_id: Ignored[int],
        task_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        date: Optional[DateTimeString] = None,
        duration_minutes: Optional[int] = None,
        status: Optional[str] = None,
        address: Optional[str] = None,
        opportunity_id: Optional[int] = None,
        contact_ids_to_add: Optional[str] = None,
        contact_ids_to_remove: Optional[str] = None
    ) -> Meet:
        """
        Actualiza la información de una reunión registrada por el usuario.

        Args:
         - name: Nombre de la reunión.
         - description: Descripción detallada de la reunión.
         - date: Fecha y hora de la reunión.
         - duration_minutes: Duración de la reunión en minutos.
         - status: Estado actual de la reunión. (pending, completed, cancelled)
         - address: Dirección donde se llevará a cabo la reunión.
         - opportunity_id: ID de la oportunidad relacionada con la reunión.
         - contact_ids_to_add: IDs de los contactos que se van a agregar a la reunión. (Si son varios, se separan por comas)
         - contact_ids_to_remove: IDs de los contactos que se van a eliminar de la reunión. (Si son varios, se separan por comas)

        Returns:
            - Meet: La reunión actualizada.
        """
        meet = MeetController.get_meet(db, user_id, task_id)

        if not meet:
            return None

        if name:
            meet.name = name
        if description:
            meet.description = description
        if date:
            meet.date = datetime.fromisoformat(date)
        if duration_minutes:
            meet.duration_minutes = duration_minutes
        if status:
            meet.status = status
        if address:
            meet.address = address
        if opportunity_id:
            meet.opportunity_id = opportunity_id


        if contact_ids_to_add:
            for contact_id in contact_ids_to_add.split(','):
                new_meet_contact = MeetContact(
                    meet_id=meet.id,
                    contact_id=int(contact_id)
                )
                db.add(new_meet_contact)
        
        if contact_ids_to_remove:
            for contact_id in contact_ids_to_remove.split(','):
                meet_contact = db.exec(select(MeetContact).where(
                    MeetContact.meet_id == meet.id,
                    MeetContact.contact_id == int(contact_id)
                )).first()
                if meet_contact:
                    db.delete(meet_contact)

        db.commit()
        db.refresh(meet)

        return meet
    

    @staticmethod
    def delete_meet(
        db: Ignored[Session],
        user_id: Ignored[int],
        meet_id: int
    ) -> Meet:
        """
        Elimina una reunión registrada por el usuario.

        Args:
         - meet_id: ID de la reunión que se desea eliminar.
        """
        meet = MeetController.get_meet(db, user_id, meet_id)

        if not meet:
            return None

        db.delete(meet)
        db.commit()

        return meet