from fastapi import APIRouter
from fastapi import HTTPException

router = APIRouter()

@router.get("/health", tags=["Health"], summary="Health Check Endpoint")
async def health_check():
    return {"status": "ok"}

@router.post("/health", tags=["Health"], summary="Exception Test Endpoint")
async def health_check_exception():
    raise HTTPException(status_code=500, detail="This is a test exception for logging purposes.")   
