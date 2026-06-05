from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AIExplanationResponse(BaseModel):
    calculation_id: int
    explanation: str

class AIRequestLogResponse(BaseModel):
    id: int
    user_id: int
    calculation_id: int
    prompt: str
    response: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIChatResponse(BaseModel):
    id: int
    user_id: int
    prompt: str
    response: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIRequest(BaseModel):
    prompt: str

class AIResponse(BaseModel):
    response: str