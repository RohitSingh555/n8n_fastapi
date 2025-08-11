"""
Database utility functions for MySQL connection
"""
import logging
from sqlalchemy import create_engine, text
import pymysql

# Ensure PyMySQL is used as the MySQL driver
pymysql.install_as_MySQLdb()

logger = logging.getLogger(__name__)

def wait_for_database(database_url: str, max_retries: int = 10, retry_interval: int = 2) -> bool:
    """
    Wait for the database to be ready before proceeding
    
    Args:
        database_url: Database connection string
        max_retries: Maximum number of retry attempts
        retry_interval: Seconds to wait between retries
    
    Returns:
        bool: True if database is ready, False otherwise
    """
    logger.info("Waiting for MySQL database to be ready...")
    
    for attempt in range(max_retries):
        try:
            # Create a temporary engine to test connection
            temp_engine = create_engine(
                database_url,
                connect_args={
                    "charset": "utf8mb4",
                    "autocommit": False,
                    "sql_mode": "STRICT_TRANS_TABLES"
                }
            )
            
            # Test the connection
            with temp_engine.connect() as conn:
                # Try to execute a simple query
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                
            logger.info(f"MySQL database is ready! (attempt {attempt + 1}/{max_retries})")
            return True
            
        except Exception as e:
            logger.warning(f"Database not ready yet (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_interval)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                return False
    
    return False

def ensure_database_exists(database_url: str) -> bool:
    """
    Ensure the database exists and is accessible
    
    Args:
        database_url: Database connection string
    
    Returns:
        bool: True if database exists and is accessible, False otherwise
    """
    try:
        # Test the connection
        temp_engine = create_engine(
            database_url,
            connect_args={
                "charset": "utf8mb4",
                "autocommit": False,
                "sql_mode": "STRICT_TRANS_TABLES"
            }
        )
        with temp_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("MySQL database connection successful")
        return True
            
    except Exception as e:
        logger.error(f"Error ensuring database exists: {str(e)}")
        return False
