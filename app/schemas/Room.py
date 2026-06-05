from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)

    length: float = Field(gt=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)

    doors_area: float = Field(default=0, ge=0)
    windows_area: float = Field(default=0, ge=0)

    room_type: Optional[str] = Field(default=None, max_length=50)


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)

    length: Optional[float] = Field(default=None, gt=0)
    width: Optional[float] = Field(default=None, gt=0)
    height: Optional[float] = Field(default=None, gt=0)

    doors_area: Optional[float] = Field(default=None, ge=0)
    windows_area: Optional[float] = Field(default=None, ge=0)

    room_type: Optional[str] = Field(default=None, max_length=50)


class RoomResponse(BaseModel):
    id: int
    name: str
    user_id: int

    length: float
    width: float
    height: float

    doors_area: float
    windows_area: float

    room_type: str = "default"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)