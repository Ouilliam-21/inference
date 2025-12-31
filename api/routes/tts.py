from typing import Dict, Callable, Optional, List
from fastapi import APIRouter
from models.models import Model

from pydantic import BaseModel


class Item(BaseModel):
    name: str

class TTSListResponse(BaseModel):
    tts: List[str]

class TTSCurrentResponse(BaseModel):
    current_tts: Optional[str]

class TTSSetCurrentResponse(BaseModel):
    status: str
    current_tts: str
    is_loaded: bool

class TTSSetCurrentError(BaseModel):
    status: str
    message: str

def create_tts_router(
    tts_models: Dict[str, Model],
    get_current_tts: Callable[[], Optional[Model]],
    set_current_tts: Callable[[Model], None],
    is_queue_empty: Callable[[], bool]
    ) -> APIRouter:
    tts_router = APIRouter()
        
    @tts_router.get("/list", tags=["tts"])
    async def list():
        return TTSListResponse(tts=[str(k) for k in tts_models.keys()])

    @tts_router.get("/", tags=["tts"])
    async def get_current():
        return TTSCurrentResponse(current_tts=get_current_tts().model_name)

    @tts_router.put("/", tags=["tts"])
    async def set_current(item: Item):

        if not is_queue_empty():
            return TTSSetCurrentError(
                status="error",
                message="Queue is not empty"
            )

        current = get_current_tts()
        if current is not None and current.is_loaded:
            current.unload()

        new_model = tts_models[item.name]
        if not new_model.is_loaded:
            new_model.load()
    
        set_current_tts(new_model)

        return TTSSetCurrentResponse(
            status="success",
            current_tts=new_model.model_name,
            is_loaded=new_model.is_loaded
        )
    
    return tts_router