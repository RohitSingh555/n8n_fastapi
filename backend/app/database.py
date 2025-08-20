from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app/n8n_database.sqlite")
logger.info(f"Using database URL: {DATABASE_URL}")


try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  
        echo=False,  
        pool_pre_ping=True
    )
    logger.info("SQLite database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def recreate_engine():
    """Recreate the database engine if needed"""
    global engine, SessionLocal
    try:
        logger.info("Recreating SQLite database engine...")
        engine.dispose()
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False,
            pool_pre_ping=True
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("SQLite database engine recreated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to recreate database engine: {e}")
        return False 