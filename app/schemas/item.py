from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.item import PriorityLevel, TaskStatus


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task item")
    description: Optional[str] = Field(None, description="Detailed description")
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Task priority level")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[TaskStatus] = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ItemStats(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    high_priority: int
