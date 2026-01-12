from asyncio import create_task
from fastapi import FastAPI
from dependencies.state import get_app_state, initialize_app_state
from routes import llm_router, tts_router, config_router, events_router
from services.events.service import EventService
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

class Server:

    def __init__(self, config_path: str = "server/config.yaml"):
        self.config_path = config_path

        initialize_app_state(self.config_path)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self.startup_event()
            yield
            # Shutdown
            print("🔄 Shutting down...")
        
        self.app = FastAPI(
            lifespan=lifespan,
            title="Inference API",
            description="LLM and TTS inference service with Bearer token authentication",
            version="1.0.0",
        )

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
            prompt_manager=app_state.prompt_manager
        )
        
        create_task(event_service.events_processor())
        print("✅ Background event processor started")

