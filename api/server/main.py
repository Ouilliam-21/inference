from asyncio import create_task
from fastapi import FastAPI
from dependencies.dependencies import get_app_state
from routes.LLM.routes import llm_router
from routes.TTS.routes import tts_router
from routes.config.routes import config_router
from routes.events.routes import events_router
from services.events.service import EventService
from middleware.auth import add_auth_header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

class Server:

    def __init__(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self.startup_event()
            yield
            # Shutdown
            print("🔄 Shutting down...")
        
        self.app = FastAPI(lifespan=lifespan)
        self._init_middleware()
        self._init_routes()

    def _init_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.app.middleware("http")(add_auth_header)

    def _init_routes(self):
        self.app.include_router(llm_router)
        self.app.include_router(tts_router)
        self.app.include_router(events_router)
        self.app.include_router(config_router)

    async def startup_event(self):
        """Called when the server starts (event loop is running)"""
        print("🚀 Server startup - initializing background tasks")
        
        app_state = get_app_state()
        print(f"✅ AppState initialized with {len(app_state.model_registry.llm_models)} LLM models")
        
        event_service = EventService(
            model_registry=app_state.model_registry,
            events_queue=app_state.events_queue,
            events_status=app_state.events_status,
        )
        
        create_task(event_service.events_processor())
        print("✅ Background event processor started")