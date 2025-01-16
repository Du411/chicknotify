from sqlalchemy import text
from app.dependencies.database import engine

def test_database_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("connect success !")
    except Exception as e:
        print(f"connect fail: {e}")

if __name__ == "__main__":
    test_database_connection()