# app/schemas/endpoint.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EndpointBase(BaseModel):
    name: str
    description: Optional[str] = None
    ml_model_id: int
    api_key_id: Optional[int] = None
    require_auth: bool = False
    path: str
    is_active: bool = True

class EndpointCreate(EndpointBase):
    pass

class EndpointUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    require_auth: Optional[bool] = None
    is_active: Optional[bool] = None

class EndpointResponse(EndpointBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    url: str  # Full endpoint URL
    ml_model_title: str  # Name of the associated model
    api_key: Optional[str] = None  # API key if associated

    class Config:
        from_attributes = True 