# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
import logging
from ..db.models.user import User
from ..db.crud.user_crud import UserCRUD
from ..schemas.user import UserCreate, UserUpdate, UserLogin
from ..core.security import get_password_hash, verify_password, create_access_token
from ..utils.validators import validate_username, validate_password
from ..core.config import settings
from datetime import datetime
from typing import Optional
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = UserCRUD(db)
    
    def create_user(self, user_create: UserCreate) -> User:
        """Create new user"""
        logger.info(f"Creating user: {user_create.username}")
        
        # Validate input
        username_error = validate_username(user_create.username)
        if username_error:
            logger.warning(f"Invalid username: {username_error}")
            raise HTTPException(status_code=400, detail=username_error)
        
        password_error = validate_password(user_create.password)
        if password_error:
            logger.warning(f"Invalid password: {password_error}")
            raise HTTPException(status_code=400, detail=password_error)
        
        # Check if user already exists
        if self.db.query(User).filter(User.username == user_create.username).first():
            logger.warning(f"Username already exists: {user_create.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        if self.db.query(User).filter(User.email == user_create.email).first():
            logger.warning(f"Email already exists: {user_create.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        logger.info(f"User created successfully: {user_create.username}")
        return db_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        logger.debug(f"Authenticating user: {username}")
        
        user = self.crud.get_by_username(username)
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {username}")
            return None
        
        logger.info(f"User authenticated successfully: {username}")
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create access token for user"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"Access token created for user: {data['sub']}")
        return encoded_jwt
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        logger.info(f"Updating user: {user_id}")
        
        if user_data.username:
            username_error = validate_username(user_data.username)
            if username_error:
                raise HTTPException(status_code=400, detail=username_error)
            
            # Check if username is already taken
            existing_user = self.db.query(User).filter(
                User.username == user_data.username,
                User.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already taken")
            
            user = self.crud.get_by_id(user_id)
            if user:
                user.username = user_data.username
        
        if user_data.email:
            # Check if email is already taken
            existing_user = self.db.query(User).filter(
                User.email == user_data.email,
                User.id != user_id
            ).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already taken")
            
            user = self.crud.get_by_id(user_id)
            if user:
                user.email = user_data.email
        
        if user_data.password:
            password_error = validate_password(user_data.password)
            if password_error:
                raise HTTPException(status_code=400, detail=password_error)
            
            user = self.crud.get_by_id(user_id)
            if user:
                user.hashed_password = get_password_hash(user_data.password)
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User updated successfully: {user_id}")
        return user

    def register(self, user: UserCreate):
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def login(self, form_data: OAuth2PasswordRequestForm) -> Optional[User]:
        """Authenticate user"""
        logger.debug(f"Authenticating user: {form_data.username}")
        
        user = self.crud.get_by_username(form_data.username)
        if not user:
            logger.warning(f"User not found: {form_data.username}")
            return None
        
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid password for user: {form_data.username}")
            return None
        
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {form_data.username}")
            return None
        
        logger.info(f"User authenticated successfully: {form_data.username}")
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        return self.crud.get_by_id(user_id)
