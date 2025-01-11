import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.users import User
from .base import NotificationStrategy
from app.core.config import settings
from app.models.jobs import Job

class EmailNotification(NotificationStrategy):
    def __init__(self, db: Session):
        self.db = db
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.GMAIL_SENDER
        self.password = settings.GMAIL_APP_PASSWORD.get_secret_value()

    async def send(self, user_id: int, job: Job):
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()

            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'有新任務啦: {job.title}'
            msg['From'] = self.sender_email
            msg['To'] = user.email

            html_content = f"""
            <html>
            <body>
                <p>任務: {job.title}</p>
                <p>雇主: {job.employer}</p>
                <p>地點: {job.location}</p>
                <p>薪資: {job.salary}</p>
                <p>任務內容:</p>
                <pre>{job.content}</pre>
                <p>工作時間: {job.time}</p>
                <p>連結: <a href="{job.url}">{job.url}</a></p>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.login(self.sender_email, self.password)
                server.send_message(msg)

        except smtplib.SMTPAuthenticationError as e:
            raise HTTPException(
                status_code=500,
                detail="Email authentication failed. Please check your credentials."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {str(e)}"
            )