from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import pymysql
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Ensure PyMySQL is used as the MySQL driver
try:
    pymysql.install_as_MySQLdb()
    logger.info("PyMySQL successfully installed as MySQLdb replacement")
except Exception as e:
    logger.warning(f"Could not install PyMySQL as MySQLdb replacement: {e}")

load_dotenv()

# Database URL - explicitly use pymysql dialect
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://n8n_user:n8n_password@mysql:3306/n8n_feedback")
logger.info(f"Using database URL: {DATABASE_URL}")

# Create engine with MySQL-specific configuration
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,  # Set to True for SQL debugging
        # Explicitly specify the driver to avoid MySQLdb import issues
        connect_args={
            "charset": "utf8mb4",
            "autocommit": False,
            "sql_mode": "STRICT_TRANS_TABLES"
        },
        # Force PyMySQL usage and avoid MySQLdb
        poolclass=None,
        # Additional PyMySQL configuration
        isolation_level="READ_COMMITTED"
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 