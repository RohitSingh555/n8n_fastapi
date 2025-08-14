"""
Database utility functions for SQLite connection
"""
import logging
from sqlalchemy import create_engine, text

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
    logger.info("Waiting for SQLite database to be ready...")
    
    for attempt in range(max_retries):
        try:
            # Create a temporary engine to test connection
            temp_engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False}
            )
            
            # Test the connection
            with temp_engine.connect() as conn:
                # Try to execute a simple query
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                
            logger.info(f"SQLite database is ready! (attempt {attempt + 1}/{max_retries})")
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

def ensure_database_exists(database_url: str, max_retries: int = 3, retry_interval: int = 2) -> bool:
    """
    Ensure the database exists and is accessible
    
    Args:
        database_url: Database connection string
        max_retries: Maximum number of retry attempts
        retry_interval: Seconds to wait between retries
    
    Returns:
        bool: True if database exists and is accessible, False otherwise
    """
    logger.info("Ensuring SQLite database exists and is accessible...")
    
    for attempt in range(max_retries):
        try:
            # Test the connection
            temp_engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False}
            )
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("SQLite database connection successful")
            return True
                
        except Exception as e:
            logger.warning(f"Database not accessible (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_interval)
                logger.info("Retrying database connection...")
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                return False
    
    return False
