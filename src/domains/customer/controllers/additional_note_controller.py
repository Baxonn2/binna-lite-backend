from typing import Optional
from sqlmodel import Session, select

from src.domains.customer.models.additional_note import AdditionalNote, AdditionalNoteSummarizedResponse
from src.domains.openai_integration import Ignored

class AdditionalNoteController:

    def create_additional_note(
        db: Ignored[Session],
        customer_id: int,
        title: str,
        description: str,
    ) -> AdditionalNote:
        """
        Almacena una nueva nota con el contenido y título especificado. Esto permite registrar
        información crucial para el seguimiento de un cliente. Es importante guardar notas que
        sean estrictamente relevantes para concretar ventas o mantener una relación con el cliente.
        Esto también considera que las notas deben ser claras y concisas, evitando perder
        información importante.

        Args:
         - customer_id: ID del cliente a la que se le va a agregar la nota.
         - title: Título de la nota.
         - description: Contenido de la nota.
        
        Returns:
         - AdditionalNote: la nota creada.
        """

        new_note = AdditionalNote(
            title=title,
            content=description,
            customer_establishment_id=customer_id
        )

        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        return new_note
    
    def get_all_additional_notes_summarized(
        db: Ignored[Session],
        customer_id: int
    ) -> list[AdditionalNoteSummarizedResponse]:
        """
        Obtiene todas las notas registradas para un cliente. Este método retorna sólo los títulos
        de las notas, para obtener el contenido de la nota se debe utilizar el método
        `get_additional_note`.

        Args:
         - customer_id: ID del cliente del que se quieren obtener las notas.

        Returns:
         - list[AdditionalNote]: lista con todas las notas registradas para el cliente.
        """
        query = select(
            AdditionalNote.id,
            AdditionalNote.title,
            AdditionalNote.customer_establishment_id
        ).where(
            AdditionalNote.customer_establishment_id == customer_id,
            AdditionalNote.deleted == False
        )

        return db.exec(query).all()


    def get_all_additional_notes(
        db: Ignored[Session],
        customer_id: int
    ) -> list[AdditionalNote]:
        """
        Obtiene todas las notas registradas para un cliente. Este método retorna todo el contenido
        de todas las notas. Es útil para obtener una mirada general de todas las notas registradas,
        pero hay que evitar llamarla. Solo se debe utilizar cuando sea necesario.

        Args:
         - customer_id: ID del cliente del que se quieren obtener las notas.

        Returns:
         - list[AdditionalNote]: lista con todas las notas registradas para el cliente.
        """
        query = select(AdditionalNote).where(
            AdditionalNote.customer_establishment_id == customer_id,
            AdditionalNote.deleted == False
        )

        return db.exec(query).all()

    
    def get_additional_note(
        db: Ignored[Session],
        note_id: int
    ) -> Optional[AdditionalNote]:
        """
        Obtiene una nota registrada.

        Args:
         - note_id: ID de la nota que se quiere obtener.

        Returns:
         - AdditionalNote: la nota solicitada.
        """
        query = select(AdditionalNote).where(
            AdditionalNote.id == note_id,
            AdditionalNote.deleted == False
        )

        return db.exec(query).first()

    
    def delete_additional_note(
        db: Ignored[Session],
        note_id: int
    ) -> AdditionalNote:
        """
        Elimina una nota registrada.

        Args:
         - note_id: ID de la nota que se quiere eliminar.

        Returns:
         - AdditionalNote: la nota eliminada.
        """
        note = db.get(AdditionalNote, note_id)
        note.deleted = True

        db.add(note)
        db.commit()
        db.refresh(note)

        return note
    

    def update_additional_note(
        db: Ignored[Session],
        note_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> AdditionalNote:
        """
        Actualiza una nota registrada.

        Args:
         - note_id: ID de la nota que se quiere actualizar.
         - title: Nuevo título de la nota.
         - description: Nuevo contenido de la nota.

        Returns:
            - AdditionalNote: la nota actualizada.
        """
        note = db.get(AdditionalNote, note_id)

        if title:
            note.title = title
        if description:
            note.content = description

        db.add(note)
        db.commit()
        db.refresh(note)

        return note