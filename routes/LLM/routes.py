from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from middlewares.auth import verify_token_flexible
from services.LLM.service import LLMService
from schemas.models.schema import InfoResponse, CurrentResponse,SetPayload,SetResponse

Service = Annotated[LLMService, Depends()]

llm_router = APIRouter(prefix="/llm", tags=["llm"], dependencies=[Depends(verify_token_flexible)])

@llm_router.get("/", response_model=CurrentResponse)
async def get_current_model(service: Service):
    """Get current active LLM model"""
    model = service.get_current_model()
    return CurrentResponse(current_model=model.model_name)

@llm_router.put("/switch", response_model=SetResponse)
async def switch_llm_model(
    request: SetPayload,
    service: Service,
):
    """Set current LLM model"""
    try:
        new_model = service.set_current_model(request.model_name)
                
        return SetResponse(
            current_model=new_model.model_name,
        )
    except RuntimeError as e:
        return HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@llm_router.get("/list", response_model=InfoResponse)
async def list_models(service: Service):
    """List all available LLM models"""
    return InfoResponse(models=service.list_models())