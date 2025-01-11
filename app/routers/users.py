from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import TokenSchema, UserLogin, UserData, UserProfile
from app.db.base import get_db
from app.services.user_service import UserService
from app.dependencies.auth import get_current_user

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.post("/api/user/register", response_model=dict)
async def register_user(
    user_data: UserData, 
    user_service: UserService = Depends(get_user_service)
):
    return user_service.register_user(user_data)

@router.post("/api/user/login", response_model=TokenSchema)
async def login(
    user_data: UserLogin, 
    user_service: UserService = Depends(get_user_service)
):
    return user_service.login_user(user_data)

@router.put("/api/user/update", response_model=dict)
async def update_user(
    user_data: UserData,  
    user_service: UserService = Depends(get_user_service),
    current_user: int = Depends(get_current_user)
):
    return user_service.update_user(user_data, current_user)

@router.delete("/api/users/deletemyself", response_model=dict)
async def delete_user_account(
    user_service: UserService = Depends(get_user_service),
    current_user: int = Depends(get_current_user)
):
    return await user_service.delete_user(current_user)

@router.get("/api/user/profile", response_model=UserProfile)
async def get_user_profile(
    user_service: UserService = Depends(get_user_service),
    current_user: int = Depends(get_current_user)
):
    return await user_service.get_user_profile(current_user)