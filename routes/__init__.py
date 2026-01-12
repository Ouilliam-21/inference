"""API route definitions"""
from routes.LLM.routes import llm_router
from routes.TTS.routes import tts_router
from routes.events.routes import events_router
from routes.config.routes import config_router

__all__ = ["llm_router", "tts_router", "events_router", "config_router"]