from pydantic import BaseModel, Field


class RuleRead(BaseModel):
    id: str
    name: str
    priority: int
    conditions_json: dict
    category_id: str
    is_active: bool

    model_config = {"from_attributes": True}


class RuleCreate(BaseModel):
    name: str = Field(..., max_length=255)
    priority: int = 0
    conditions_json: dict = Field(default_factory=dict)
    category_id: str


class RuleUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    priority: int | None = None
    conditions_json: dict | None = None
    category_id: str | None = None
    is_active: bool | None = None


class RuleSuggestionRead(BaseModel):
    id: str
    source_pattern: str
    suggested_conditions_json: dict
    suggested_category_id: str
    coverage_count: int
    status: str

    model_config = {"from_attributes": True}
