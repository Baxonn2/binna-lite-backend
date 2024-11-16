from datetime import datetime, UTC
from typing import Any, Dict, List, Literal, Type, Union
from fastapi.types import IncEx
from sqlmodel import Field, SQLModel
from pydantic.v1.fields import ModelField, SHAPE_LIST

def get_utc_now():
    return datetime.now(UTC)

class TimestampedModel(SQLModel):
    created_at: datetime = Field(default=datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, nullable=False)

class TimestampedModelResponse(SQLModel):
    created_at: datetime
    updated_at: datetime

class DeletableModel(SQLModel):
    deleted: bool = Field(default=False, nullable=False)

class BaseModel(TimestampedModel, DeletableModel):
    pass

# class BaseModelResponse(TimestampedModelResponse):
    
#     def model_dump(
#         self,
#         *,
#         mode: Union[Literal["json", "python"], str] = "python",
#         include: IncEx = None,
#         exclude: IncEx = None,
#         by_alias: bool = False,
#         exclude_unset: bool = False,
#         exclude_defaults: bool = False,
#         exclude_none: bool = False,
#         round_trip: bool = False,
#         warnings: bool = True,
#     ) -> Dict[str, Any]:
#         for field in self.__fields__.values():
#             field: ModelField
#             if field.shape == SHAPE_LIST:
#                 setattr(self, field.name, [
#                     item for item in self.__dict__[field.name] if (item and (item.__dict__.get("deleted", None) is not True))
#                 ])

#         return super().model_dump(
#             mode=mode,
#             include=include,
#             exclude=exclude,
#             by_alias=by_alias,
#             exclude_unset=exclude_unset,
#             exclude_defaults=exclude_defaults,
#             exclude_none=exclude_none,
#             round_trip=round_trip,
#             warnings=warnings
#         )
