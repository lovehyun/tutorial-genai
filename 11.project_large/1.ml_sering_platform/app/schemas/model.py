from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    framework: str = "sklearn"  # 기본값으로 sklearn 설정
    path: str
    is_active: bool = True

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    framework: Optional[str] = None
    path: Optional[str] = None
    is_active: Optional[bool] = None

class Model(ModelBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ModelResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    type: str
    framework: str
    path: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 