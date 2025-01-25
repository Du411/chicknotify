from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
    }
    status_code = status.HTTP_200_OK 

    return JSONResponse(content=health_status, status_code=status_code)