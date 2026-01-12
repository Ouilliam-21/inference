from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from dependencies.dependencies import get_model_registry
from services.TTS.service import TTSService
from services.events.service import EventService
from schemas.models.schema import InfoResponse, CurrentResponse,SetPayload,SetResponse

Service = Annotated[TTSService, Depends()]

tts_router = APIRouter(prefix="/tts", tags=["tts"])

@tts_router.get("/", response_model=CurrentResponse)
async def get_current_model(service: Service):
    """Get current active TTS model"""
    model = service.get_current_model()
    return CurrentResponse(current_model=model.model_name)

@tts_router.put("/", response_model=SetResponse)
async def set_current_model(
    request: SetPayload,
    service: Service,
):
    """Set current TT model"""
    try:
        new_model = service.set_current_model(request.name)
                
        return SetResponse(
            current_model=new_model.model_name,
        )
    except RuntimeError as e:
        return HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@tts_router.get("/list", response_model=InfoResponse)
async def list_models(service: Service):
    """List all available TTS models"""
    return InfoResponse(models=service.list_models())