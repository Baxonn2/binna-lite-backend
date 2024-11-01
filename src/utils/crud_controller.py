from typing import Any, Dict, Optional, Self, Type, TypeVar, Generic
from sqlmodel import Session, select

T = TypeVar("T")
E = TypeVar("E")
class CRUDController(Generic[T, E]):
    def __init__(
        self,
        model: Type[T],
        required_params: list[str] = [],
        unique_fields: list[str] = [],
        extended_model: Optional[Type[E]] = None
    ):
        self.model = model
        self.model_type = type(model)
        self.required_params = required_params
        self.unique_fields = unique_fields
        self.extended_model = extended_model

    def get_all(self, db: Session, params: dict = {}) -> list[T]:
        query = select(self.model).where(self.model.deleted == False)

        for param_name in self.required_params:
            query = query.where(
                getattr(self.model, param_name) == params[param_name]
            )

        return db.exec(query).all()

    def get(
        self,
        db: Session,
        id: int,
        params: dict = {},
        extra_filters: Dict[str, Any] = {},
    ) -> T:
        query = select(self.model).where(self.model.id == id, self.model.deleted == False, *[
            getattr(self.model, param_name) == params[param_name] for param_name in self.required_params
        ])

        for key, value in extra_filters.items():
            query = query.where(getattr(self.model, key) == value)

        return db.exec(query).first()
    
    def get_extended(
        self,
        db: Session,
        id: int,
        params: dict = {},
        extra_filters: Dict[str, Any] = {},
    ) -> E:
        result = self.get(db, id, params, extra_filters)

        if self.extended_model is None:
            raise Exception("Extended model not defined")

        return self.extended_model.model_validate(result)
    
    def create(self, db: Session, data: dict) -> T:
        for field in self.unique_fields:
            query = select(self.model).where(
                getattr(self.model, field) == data[field]
            ).where(self.model.deleted == False)
            if db.exec(query).first():
                raise Exception(f"{field} already exists")

        element_instance = self.model(**data)

        db.add(element_instance)
        db.commit()
        db.refresh(element_instance)
        return element_instance
    
    def update(self, db: Session, id: int, data: dict) -> T:
        query = select(self.model).where(
            self.model.id == id,
            self.model.deleted == False
        )
        element_instance = db.exec(query).first()

        if element_instance is None:
            raise Exception("Element not found")

        for key, value in data.items():
            setattr(element_instance, key, value)

        db.commit()
        db.refresh(element_instance)
        return element_instance
    
    def delete(self, db: Session, id: list[int]) -> bool:
        query = select(self.model).where(self.model.id.in_(id))
        element_instances = db.exec(query).all()
        for element_instance in element_instances:
            print("Deleting element", element_instance.id)
            element_instance.deleted = True
            db.commit()
            db.refresh(element_instance)
        return True