
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

class OperationType(str, Enum):
    MEAN = "mean"
    SUM = "sum"
    MULTIPLY = "multiply"
    ADD = "add"

class ComputationRequest(BaseModel):
    data_id: str = Field(..., description="Data identifier")
    operation: OperationType = Field(..., description="Operation type")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Operation parameters")

class ComputationResponse(BaseModel):
    task_id: str
    status: str

class TaskStatusResponse(BaseModel):
    id: str
    type: str
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error: Optional[str]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

