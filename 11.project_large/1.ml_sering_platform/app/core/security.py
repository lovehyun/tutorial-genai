from datetime import datetime, timedelta
from typing import Optional
import secrets
import string
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def generate_api_key(length: int = 32) -> str:
    """API 키 생성
    
    Args:
        length (int): API 키 길이 (기본값: 32)
    
    Returns:
        str: 생성된 API 키
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def verify_api_key(api_key: str, stored_key: str) -> bool:
    """API 키 검증
    
    Args:
        api_key (str): 검증할 API 키
        stored_key (str): 저장된 API 키
    
    Returns:
        bool: API 키가 일치하면 True, 아니면 False
    """
    return secrets.compare_digest(api_key, stored_key) 