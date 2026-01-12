from asyncio.queues import Queue
from typing import Annotated, List, Dict

from fastapi import Depends
from dependencies.state import get_events_queue, get_model_registry
from ai.models.registry import ModelRegistry
from ai.models.models import Model
from database.models import ProcessingRiotEventJob

class LLMService:
    """Service for managing LLM models"""
    
    def __init__(
        self, 
        model_registry: Annotated[ModelRegistry, Depends(get_model_registry)],
        events_queue: Annotated[Queue[ProcessingRiotEventJob], Depends(get_events_queue)]
    ):
        self._model_registry = model_registry
        self._events_queue = events_queue
    
    def list_models(self) -> List[str]:
        """Get list of available models"""
        return list(self._model_registry.llm_models.keys())
    
    def get_current_model(self) -> Model:
        """Get currently active model"""
        return self._model_registry.current_llm
    
    def set_current_model(self, model_name: str) -> Model:
        """Switch to a different model"""
        if model_name not in self._model_registry.llm_models:
            raise ValueError(f"Model {model_name} not found")
        
        if not self._events_queue.empty():
            raise RuntimeError("Cannot switch models while queue is not empty")
        
        self._model_registry.current_llm.unload()
        
        new_model = self._model_registry.llm_models[model_name]
        new_model.load()
        
        self._model_registry.current_llm = new_model
        
        return new_model
    
    def is_queue_empty(self) -> bool:
        """Check if processing queue is empty"""
        return self._events_queue.empty()