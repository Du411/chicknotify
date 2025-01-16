from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.models.users import User
from app.dependencies.database import get_db

security = HTTPBearer()

async def get_current_user(
    token = Depends(security),
    db: Session = Depends(get_db)
) -> int:
    payload = verify_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.user_id == user_id).first()
    return user.user_id