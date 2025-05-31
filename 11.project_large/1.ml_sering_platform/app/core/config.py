from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    # 프로젝트 기본 설정
    PROJECT_NAME: str = "ML Serving Platform"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Machine Learning Model Serving Platform API"
    API_V1_STR: str = "/api/v1"
    
    # 보안 설정
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 데이터베이스 설정
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Redis 설정
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS 설정
    CORS_ORIGINS: List[str] = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # 파일 업로드 설정
    UPLOAD_DIR: str = "uploads"
    MODEL_DIR: str = os.path.join(UPLOAD_DIR, "models")  # uploads/models 디렉토리
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        case_sensitive = True

# 설정 인스턴스 생성
settings = Settings()

# 업로드 및 모델 디렉토리 생성
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODEL_DIR, exist_ok=True) 