from asyncio.queues import Queue
from typing import Optional
from database.models import ProcessingRiotEventJob
from models.registry import ModelRegistry

class AppState:
    """Application-wide state container"""
    
    def __init__(self):
        self.model_registry = ModelRegistry()
        self.events_queue = Queue[ProcessingRiotEventJob]()
        self.events_status = Queue[ProcessingRiotEventJob]()

_app_state: Optional[AppState] = None

def get_app_state() -> AppState:
    """Get or create the application state singleton"""
    global _app_state
    if _app_state is None:
        _app_state = AppState()
    return _app_state


def get_model_registry() -> ModelRegistry:
    """Dependency for model registry"""
    return get_app_state().model_registry

def get_events_queue() -> Queue[ProcessingRiotEventJob]:
    """Dependency for events queue"""
    return get_app_state().events_queue


def get_events_status() -> Queue[ProcessingRiotEventJob]:
    """Dependency for events status queue"""
    return get_app_state().events_status
