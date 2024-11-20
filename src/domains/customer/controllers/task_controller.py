from sqlmodel import Session, select
from typing import Optional
from datetime import datetime

from src.domains.openai_integration import Ignored, DateTimeString
from src.domains.customer.models.task import Task


class TaskController:

    @staticmethod
    def create_task(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: int,
        name: str,
        description: str,
        due_date: Optional[DateTimeString] = None,
        completed: Optional[bool] = False,
    ) -> Task:
        """
        Registra una nueva tarea en la base de datos del usuario.

        Args:
         - customer_id: ID del cliente al que está relacionada la tarea.
         - name: Nombre de la tarea que se va a registrar.
         - description: Descripción detallada de la tarea.
         - due_date: Fecha y hora de vencimiento de la tarea. (Formato ISO 8601)
         - completed: Indica si la tarea ya fue completada.

        Returns:
         - Task: La nueva tarea registrada.
        """
        parsed_due_date = datetime.fromisoformat(due_date) if due_date else None

        new_task = Task(
            name=name,
            description=description,
            due_date=parsed_due_date,
            completed=completed,
            user_id=user_id,
            establishment_id=customer_id
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task
    
    @staticmethod
    def get_all_tasks(
        db: Ignored[Session],
        user_id: Ignored[int],
        customer_id: Optional[int] = None
    ) -> list[Task]:
        """
        Obtiene todas las tareas registradas por el usuario.

        Args:
         - customer_id: ID del cliente al que están relacionadas las tareas.

        Returns:
         - list[Task]: lista con todas las tareas registradas por el usuario.
        """
        query = select(Task).where(
            Task.user_id == user_id,
            Task.deleted == False
        )

        if customer_id:
            query = query.where(Task.establishment_id == customer_id)

        return db.exec(query).all()
    
    
    @staticmethod
    def get_task(
        db: Ignored[Session],
        user_id: Ignored[int],
        task_id: int
    ) -> Task:
        """
        Obtiene una tarea registrada por el usuario.

        Args:
         - task_id: ID de la tarea que se va a obtener.

        Returns:
         - Task: La tarea solicitada.
        """
        query = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
            Task.deleted == False
        )

        return db.exec(query).first()
    
    
    @staticmethod
    def update_task(
        db: Ignored[Session],
        user_id: Ignored[int],
        task_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[DateTimeString] = None,
        completed: Optional[bool] = None
    ) -> Task:
        """
        Actualiza los datos de una tarea registrada por el usuario.

        Args:
         - task_id: ID de la tarea que se va a actualizar.
         - name: Nuevo nombre de la tarea.
         - description: Nueva descripción detallada de la tarea.
         - due_date: Nueva fecha y hora de vencimiento de la tarea. (Formato ISO 8601)
         - completed: Indica si la tarea ya fue completada.

        Returns:
         - Task: La tarea actualizada.
        """
        task = TaskController.get_task(db, user_id, task_id)

        if not task:
            return None

        if name:
            task.name = name
        if description:
            task.description = description
        if due_date:
            task.due_date = datetime.fromisoformat(due_date)
        if completed is not None:
            task.completed = completed

        db.commit()
        db.refresh(task)

        return task
    
    
    @staticmethod
    def delete_task(
        db: Ignored[Session],
        user_id: Ignored[int],
        task_id: int
    ) -> Task:
        """
        Elimina una tarea registrada por el usuario.

        Args:
         - task_id: ID de la tarea que se va a eliminar.

        Returns:
         - Task: La tarea eliminada.
        """
        task = TaskController.get_task(db, user_id, task_id)

        if not task:
            return None

        task.deleted = True

        db.commit()
        db.refresh(task)

        return task