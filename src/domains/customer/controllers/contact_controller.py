from typing import Optional
from sqlmodel import Session, select
from src.domains.customer.models.contact import Contact
from src.domains.openai_integration import Ignored

class ContactController:

    @staticmethod
    def create_contact(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: int,
        name: str,
        role: str,
        email: str,
        phone: str
    ) -> Contact:
        """
        Registra un nuevo contacto de un cliente en la base de datos del usuario.

        Args:
         - customer_id: ID del cliente al que se le va a agregar el contacto. Este no debe ser solicitado al usuario como tal, se puede extraer sabiendo el nombre del cliente.
         - name: Nombre del contacto.
         - role: Rol del contacto.
         - email: Correo del contacto.
         - phone: Teléfono del contacto.

        Returns:
         - Contact: El nuevo contacto registrado.
        """
        new_contact = Contact(
            user_id=user_id,
            establishment_id=customer_id,
            name=name,
            role=role,
            email=email,
            phone=phone
        )

        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)

        return new_contact
    

    @staticmethod
    def get_all_contacts(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: Optional[int] = None
    ) -> list[Contact]:
        """
        Obtiene todos los contactos registrados por el usuario.

        Args:
         - customer_id: ID del cliente al que pertenecen los contactos.

        Returns:
         - list[Contact]: lista con todos los contactos registrados por el usuario.
        """
        query = select(Contact).where(
            Contact.user_id == user_id,
            Contact.deleted == False,
        )

        if customer_id:
            query = query.where(Contact.establishment_id == customer_id)

        return db.exec(query).all()
    
    @staticmethod
    def get_contact(
        db: Ignored[Session],
        user_id: Ignored[int],
        contact_id: int
    ) -> Contact:
        """
        Obtiene un contacto registrado por el usuario.

        Args:
         - contact_id: ID del contacto a obtener.

        Returns:
         - Contact: El contacto registrado por el usuario.
        """
        query = select(Contact).where(
            Contact.user_id == user_id,
            Contact.id == contact_id,
            Contact.deleted == False
        )

        return db.exec(query).first()
    
    
    @staticmethod
    def update_contact(
        db: Ignored[Session],
        user_id: Ignored[int],
        contact_id: int,
        name: Optional[str] = None,
        role: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Contact:
        """
        Actualiza un contacto registrado por el usuario.

        Args:
         - contact_id: ID del contacto a actualizar.
         - name: Nombre del contacto.
         - role: Rol del contacto.
         - email: Correo del contacto.
         - phone: Teléfono del contacto.

        Returns:
         - Contact: El contacto actualizado.
        """
        contact = ContactController.get_contact(db, user_id, contact_id)

        if contact is None:
            return None
        
        if name is not None:
            contact.name = name
        if role is not None:
            contact.role = role
        if email is not None:
            contact.email = email
        if phone is not None:
            contact.phone = phone

        db.add(contact)
        db.commit()
        db.refresh(contact)

        return contact
    
    
    @staticmethod
    def delete_contact(
        db: Ignored[Session],
        user_id: Ignored[int],
        contact_id: int
    ) -> Contact:
        """
        Elimina un contacto registrado por el usuario.

        Args:
         - contact_id: ID del contacto a eliminar.

        Returns:
         - Contact: El contacto eliminado.
        """
        contact = ContactController.get_contact(db, user_id, contact_id)

        if contact is None:
            return None
        
        contact.deleted = True

        db.add(contact)
        db.commit()
        db.refresh(contact)

        return contact