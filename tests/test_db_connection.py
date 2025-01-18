from sqlalchemy import text
from app.dependencies.database import engine
from app.core.logger import logger
def test_database_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("connect success !")
    except Exception as e:
        logger.error(f"connect fail: {e}")

if __name__ == "__main__":
    test_database_connection()