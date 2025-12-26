from typing import Dict
from fastapi import APIRouter
from models.models import Model
from typing import Dict, Callable, Optional
from pydantic import BaseModel


class Item(BaseModel):
    name: str

def create_llm_router(
    llm_models: Dict[str, Model],
    get_current_llm: Callable[[], Optional[Model]],
    set_current_llm: Callable[[Model], None]
    ) -> APIRouter:
    llm_router = APIRouter()
        
    @llm_router.get("/llm/list", tags=["llm"])
    async def list():
        return {"llm": list(llm_models.keys())}

    @llm_router.get("/llm", tags=["llm"])
    async def get_current():
        current = get_current_llm()
        if current is None:
            return {"current_tts": None}
        return {"current_tts": current.model_name}

    @llm_router.put("/llm", tags=["llm"])
    async def set_current(item: Item):
        current = get_current_llm()
        if current is not None and current.is_loaded:
            current.unload()

        new_model = llm_models[item.name]
        if not new_model.is_loaded:
            new_model.load()
    
        set_current_llm(new_model)

        return {
            "status": "success",
            "current_llm": new_model.model_name,
            "is_loaded": new_model.is_loaded
        }
    

    return llm_router