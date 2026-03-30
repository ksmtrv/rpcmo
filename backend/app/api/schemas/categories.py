from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    type: str
    color: str | None = None


class CategoryRead(BaseModel):
    id: str
    name: str
    type: str
    color: str | None
    is_system: bool

    model_config = {"from_attributes": True}


class CategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
