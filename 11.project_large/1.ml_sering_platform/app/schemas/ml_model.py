# app/schemas/ml_model.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MLModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    ml_type: str
    framework: str

class MLModelCreate(MLModelBase):
    pass

class MLModelUpdate(MLModelBase):
    pass

class MLModel(MLModelBase):
    id: int
    file_path: str
    file_size: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    
    model_config = {
        'from_attributes': True  # 이 설정만 유지 (ORM 모델 변환을 위해 필요)
    }
