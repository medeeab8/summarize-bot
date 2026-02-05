from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"], summary="Health Check Endpoint")
async def health_check():
    return {"status": "ok"}