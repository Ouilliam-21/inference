from asyncio.queues import Queue
from pathlib import Path, PurePath
from typing import Optional
from database.models import ProcessingRiotEventJob
from ai.models.registry import ModelRegistry
from ai.prompts.manager import PromptManager

class AppState:
    """Application-wide state container"""
    
    def __init__(self, path: str):
        self.model_registry = ModelRegistry()
        self.events_queue = Queue[ProcessingRiotEventJob]()
        self.events_status = Queue[ProcessingRiotEventJob]()
        self.prompt_manager = PromptManager(path)


def initialize_app_state(config_path: str) -> None:
    """Initialize app state with config path."""
    global _app_state
    if _app_state is None:
        config_path_obj = Path(config_path)
        if not config_path_obj.is_absolute():
            config_path_obj = Path.cwd() / config_path_obj
        
        _app_state = AppState(str(config_path_obj))
        print(f"📝 Config path: {config_path_obj}")

_app_state: Optional[AppState] = None

def get_app_state() -> AppState:
    """Get or create the application state singleton"""
    global _app_state
    if _app_state is None:
        default_path = Path.cwd() / "server" / "config.yaml"
        _app_state = AppState(str(default_path))
        print(f"⚠️  AppState not initialized, using default: {default_path}")
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

def get_prompt_manager() -> PromptManager:
    """Dependency for events prompt manager"""
    return get_app_state().prompt_manager
