from typing import Dict, Callable, Optional
from fastapi import APIRouter
from models.models import Model

from pydantic import BaseModel


class Item(BaseModel):
    name: str


def create_tts_router(
    tts_models: Dict[str, Model],
    get_current_tts: Callable[[], Optional[Model]],
    set_current_tts: Callable[[Model], None]
    ) -> APIRouter:
    tts_router = APIRouter()
        
    @tts_router.get("/tts/list", tags=["tts"])
    async def list():
        return {"tts": list(tts_models.keys())}

    @tts_router.get("/tts", tags=["tts"])
    async def get_current():
        current = get_current_tts()
        if current is None:
            return {"current_tts": None}
        return {"current_tts": current.model_name}

    @tts_router.put("/tts", tags=["tts"])
    async def set_current(item: Item):
        current = get_current_tts()
        if current is not None and current.is_loaded:
            current.unload()

        new_model = tts_models[item.name]
        if not new_model.is_loaded:
            new_model.load()
    
        set_current_tts(new_model)

        return {
            "status": "success",
            "current_tts": new_model.model_name,
            "is_loaded": new_model.is_loaded
        }

    
    return tts_router