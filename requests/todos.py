from pydantic import BaseModel, Field
from typing import Optional


class ToDoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=3, max_length=255)
    priority: int = Field(gt=0, lt=6)
    complete: Optional[bool] = Field(default=False)
