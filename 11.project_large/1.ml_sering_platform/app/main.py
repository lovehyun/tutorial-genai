# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
import os
from .core.config import settings
from .api import auth, models, endpoints, api_keys, inference
from .db.session import engine
from .db.base import Base
from .core.redis_client import init_redis, close_redis
import logging
import uvicorn
from logging.handlers import RotatingFileHandler

# API prefix 설정
API_PREFIX = "/api/v1"

# 로그 디렉토리 생성
os.makedirs("logs", exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            "logs/app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()  # 콘솔 출력도 유지
    ]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# FastAPI 라우팅 디버그 로그 활성화
logging.getLogger("fastapi").setLevel(logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ML Model Serving Platform",
    description="A platform for serving machine learning models",
    version="0.1.0",
    redirect_slashes=True
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 422 에러 핸들러 추가
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

# API 라우터 등록
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(models.router, prefix=API_PREFIX)
app.include_router(endpoints.router, prefix=API_PREFIX)
app.include_router(api_keys.router, prefix=API_PREFIX)
app.include_router(inference.router, prefix=API_PREFIX)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("Starting up application...")
    init_redis()  # Synchronous Redis initialization

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("Shutting down application...")
    close_redis()  # Synchronous Redis cleanup

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Welcome to ML Model Serving Platform API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/inference")
async def read_inference():
    with open("frontend/inference.html") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True, log_level="debug")
