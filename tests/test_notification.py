import asyncio
from datetime import datetime
from app.dependencies.database import get_db
from app.models.jobs import Job
from app.services.notifications.email import EmailNotification
from app.models.users import User
from app.core.logger import logger

async def test_email_notification():
    db = next(get_db())
    
    try:
        test_job = Job(
            title="test",
            employer="林小姐",
            location="wfh",
            salary="250/h",
            content="test",
            url="https://example.com/test-job",
            time="2025-01-10",
            created_at=datetime.now()
        )
        test_user = db.query(User).filter(User.username == 'testuser').first()          
        email_notification = EmailNotification(db)
        await email_notification.send(
            user_id=test_user.user_id,
            job=test_job,
        )
        
        logger.info(f"mail sent to: {test_user.email} successfully")
        
    except Exception as e:
        logger.error(f"error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_email_notification())
