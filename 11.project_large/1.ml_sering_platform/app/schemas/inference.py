# app/schemas/inference.py
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class InferenceRequest(BaseModel):
    id: int
    input_data: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None

class InferenceResponse(BaseModel):
    task_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None
    id: int
    name: str

class InferenceResult(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
