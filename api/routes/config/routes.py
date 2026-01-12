from fastapi import APIRouter

from schemas.config.schema import HealthResponse

config_router = APIRouter(prefix="/config", tags=["config"])
    
@config_router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="success")

