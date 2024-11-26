from typing import Optional
from sqlmodel import Session, update, select
from src.domains.auth.models.user import User

from src.domains.openai_integration import Ignored

class UserController:

    @staticmethod
    def get_user_profile(
        db: Ignored[Session],
        user_id: Ignored[int]
    ) -> User:
        """
        Obtiene la información del usuario.

        Returns:
         - User: El usuario.
        """
        
        query = select(User).where(
            User.id == user_id,
        )
        user = db.exec(query).first()
        return user

    @staticmethod
    def update_user_profile(
        db: Ignored[Session],
        user_id: Ignored[int],
        user_business_description: Optional[str] = None,
        user_first_name: Optional[str] = None,
        user_last_name: Optional[str] = None,
        user_biography: Optional[str] = None
    ) -> User:
        """
        Actualiza la información del usuario.

        Args:
        - user_business_description: Descripción del negocio del usuario. Acá se puede incluir 
        información sobre el tipo de negocio, la ubicación, la misión, la visión, los valores, los
        productos y servicios que ofrece, entre otros.
        - user_first_name: Nombre del usuario.
        - user_last_name: Apellido del usuario.
        - user_biography: Biografía del usuario. Acá se puede incluir el cargo que ocupa, la
        experiencia laboral, los estudios realizados, los proyectos en los que ha trabajado, entre
        otros.

        Returns:
         - User: El usuario actualizado.
        """
        
        user = UserController.get_user_profile(db, user_id)

        if not user:
            return None

        if user_business_description:
            user.my_business_description = user_business_description
        if user_first_name:
            user.first_name = user_first_name
        if user_last_name:
            user.last_name = user_last_name
        if user_biography:
            user.biography = user_biography

        db.commit()
        db.refresh(user)
        
        return user