import uuid
from pydantic import BaseModel


class CoreModel(BaseModel):
    pass


class IDModelMixin(BaseModel):
    id: uuid.UUID


class StatusResponse(CoreModel):
    status: str
