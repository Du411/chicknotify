from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.users import User
from app.models.user_subscriptions import UserSubscription
from app.models.notifications import Notification
from app.models.notification_types import NotificationType
from app.core.security import verify_password, create_jwt_token, get_password_hash
from app.schemas.auth import UserRegister, UserUpdate, UserLogin
from app.schemas.notification import NotificationPreference

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserRegister):
        if self.db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username is already used"
            )
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            telegram_id=user_data.telegram_id,
            discord_id=user_data.discord_id,
            notification_type_id=user_data.notification_type_id
        )
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return {"message": "register success"}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def login_user(self, user_data: UserLogin):
        user = self.db.query(User).filter(User.username == user_data.username).first()
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        access_token = create_jwt_token(subject=user.user_id)
        return {
            "token_type": "bearer",
            "access_token": access_token
        }

    def update_user(self, user_data: UserUpdate, current_user_id: int):
        user = self.db.query(User).filter(User.user_id == current_user_id).first()

        if user_data.password:
            if not user_data.old_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Old password is required when updating password"
                )
            if not verify_password(user_data.old_password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Old password is incorrect"
                )

        if user_data.telegram_id:
            existing_telegram = self.db.query(User).filter(
                User.telegram_id == user_data.telegram_id,
                User.user_id != current_user_id
            ).first()
            if existing_telegram:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Telegram ID already in use"
                )

        if user_data.discord_id:
            existing_discord = self.db.query(User).filter(
                User.discord_id == user_data.discord_id,
                User.user_id != current_user_id
            ).first()
            if existing_discord:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Discord ID already in use"
                )

        try:
            if user_data.email:
                user.email = user_data.email
            if user_data.password:
                user.password = get_password_hash(user_data.password)
            if user_data.telegram_id:
                user.telegram_id = user_data.telegram_id
            if user_data.discord_id:
                user.discord_id = user_data.discord_id
            if user_data.notification_type_id:
                user.notification_type_id = user_data.notification_type_id

            self.db.commit()
            self.db.refresh(user)
            return {"message": "update success"}
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def get_user_notification_preferences(self, user_id: int) -> NotificationPreference:
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        notification_type = self.db.query(NotificationType).filter(
            NotificationType.id == user.notification_type_id
        ).first()
        return NotificationPreference(
            user_id=user_id,
            notification_type=notification_type.type,
            description=notification_type.description or ""
        )

    async def delete_user(self, user_id: int) -> dict:
        try:
            self.db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id
            ).delete()
            self.db.query(Notification).filter(
                Notification.user_id == user_id
            ).delete()
            
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            self.db.delete(user)
            self.db.commit()
            
            return {"message": "User and all related data deleted successfully"}
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_user_profile(self, user_id: int):
        user = self.db.query(User).filter(User.user_id == user_id).first()
        return user
