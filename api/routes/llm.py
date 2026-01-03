from typing import Dict, List
from fastapi import APIRouter, Request
from models.models import Model
from typing import Dict, Callable, Optional
from pydantic import BaseModel


class Item(BaseModel):
    name: str
class LLMListResponse(BaseModel):
    llm: List[str]

class LLMCurrentResponse(BaseModel):
    current_llm: Optional[str]

class LLMSSetCurrentResponse(BaseModel):
    status: str
    current_llm: str
    is_loaded: bool

class LLMSSetCurrentError(BaseModel):
    status: str
    message: str

def create_llm_router(
    llm_models: Dict[str, Model],
    get_current_llm: Callable[[], Optional[Model]],
    set_current_llm: Callable[[Model], None],
    is_queue_empty: Callable[[], bool]
    ) -> APIRouter:
    llm_router = APIRouter()
        
    @llm_router.get("/list", tags=["llm"])
    async def list():
        return LLMListResponse(llm=[str(k) for k in llm_models.keys()])
    
    @llm_router.get("/", tags=["llm"])
    async def get_current():
        return LLMCurrentResponse(current_llm=get_current_llm().model_name)

    @llm_router.put("/", tags=["llm"])
    async def set_current(item: Item):

        if not is_queue_empty():
            return LLMSSetCurrentError(
                status="error",
                message="Queue is not empty"
            )

        current = get_current_llm()
        current.unload()

        new_model = llm_models[item.name]
        new_model.load()
    
        set_current_llm(new_model)

        return LLMSSetCurrentResponse(
            status="success",
            current_llm=new_model.model_name,
            is_loaded=new_model.is_loaded
        )
    

    return llm_router