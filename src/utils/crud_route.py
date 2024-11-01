from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from typing import Optional, Any
from domains.auth.models.user import User
from src.domains.auth.controller import get_current_active_user
from src.database.database import Database

class CRUDRouteFactory:
    def __init__(
        self,
        model: Any,
        response_model: Any,
        base_model: Any,
        database: Database,
        prefix: str = ""
    ):
        self.model = model
        self.response_model = response_model
        self.base_model = base_model
        self.database = database
        self.router = APIRouter(
            prefix=prefix,
            dependencies=[Depends(get_current_active_user)]
        )
    
        self.router_params = []
        for index, element in enumerate(prefix.split("/")):
            if "{" in element:
                param_name = element.replace("{", "").replace("}", "")
                self.router_params.append(param_name)

    def create(self):
        @self.router.get("/")
        async def get_all_elements(
            request: Request,
            user: User = Depends(get_current_active_user),
            db: Session = Depends(self.database.get_db_session)
        ):
            query = select(self.model).where(self.model.deleted == False)

            for param_name in self.router_params:
                query = query.where(
                    getattr(self.model, param_name) == request.path_params[param_name]
                )

            return db.exec(query).all()

        @self.router.get("/{id}", response_model=self.response_model)
        async def get_element(
            id: int,
            request: Request,
            db: Session = Depends(self.database.get_db_session)
        ):
            query = select(self.model).where(self.model.id == id, *[
                getattr(self.model, param_name) == request.path_params[param_name] for param_name in self.router_params
            ])

            self.response_model.update_forward_refs()
            return db.exec(query).first()
        
        @self.router.post("/")
        async def create_element(
            element: self.base_model,
            request: Request,
            db: Session = Depends(self.database.get_db_session)
        ):
            element_instance = self.model(
                **element.model_dump(),
                **{param_name: request.path_params[param_name] for param_name in self.router_params}
            )
            
            db.add(element_instance)
            db.commit()
            db.refresh(element_instance)
            
            return element_instance
        
        @self.router.put("/{id}")
        async def update_element(
            id: int,
            element: self.base_model,
            request: Request,
            db: Session = Depends(self.database.get_db_session)
        ):
            query = select(self.model).where(self.model.id == id, *[
                getattr(self.model, param_name) == request.path_params[param_name] for param_name in self.router_params
            ])
            element_instance = db.exec(query).first()

            if element_instance is None:
                return HTTPException(status_code=404, detail="Element not found")
            
            for key, value in element.dict().items():
                setattr(element_instance, key, value)
            
            db.commit()
            db.refresh(element_instance)
            
            return element_instance
        
        @self.router.delete("/{id}")
        async def delete_element(
            id: int,
            request: Request,
            db: Session = Depends(self.database.get_db_session)
        ):
            query = select(self.model).where(self.model.id == id, *[
                getattr(self.model, param_name) == request.path_params[param_name] for param_name in self.router_params
            ])
            element_instance = db.exec(query).first()

            if element_instance is None:
                return HTTPException(status_code=404, detail="Element not found")
            
            element_instance.deleted = True
            db.commit()
            db.refresh(element_instance)
            
            return element_instance
        return self.router