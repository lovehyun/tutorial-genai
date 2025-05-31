# scripts/create_admin.py
"""
Create admin user script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.db.models.user import User
from app.db.models.model import Model
from app.db.models.api_key import APIKey
from app.core.security import get_password_hash
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user():
    """Create admin user"""
    db = None
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            logger.info("Admin user exists, updating password...")
            admin_user.hashed_password = get_password_hash("admin")
            db.commit()
            logger.info("Admin password updated to 'admin'")
            return
        
        # Create admin user
        admin_password = "admin"  # Change this in production
        hashed_password = get_password_hash(admin_password)
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password
        )
        
        db.add(admin_user)
        db.commit()
        
        logger.info(f"Admin user created: username='admin', password='admin'")
        logger.warning("Please change the admin password in production!")
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        raise
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    create_admin_user()
