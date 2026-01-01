from routes.llm import create_llm_router
from routes.tts import create_tts_router
from routes.queue import create_event_router
from routes.heath import create_health_router

__all__ = [create_event_router, create_llm_router, create_tts_router, create_health_router]