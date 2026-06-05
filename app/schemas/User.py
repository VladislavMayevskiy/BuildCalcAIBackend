from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic import conint


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)