from fastapi import APIRouter


def create_health_router() -> APIRouter:
    llm_router = APIRouter()
        
    @llm_router.get("/", tags=["health"])
    async def health():
        return {"status": "success"}

    return llm_router