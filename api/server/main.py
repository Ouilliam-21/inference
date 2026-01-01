from asyncio import Queue
from fastapi import FastAPI
from middleware.auth import add_auth_header
from models.llm.DolphinGGUF import DolphinGGUF
from models.models import Model
from routes import create_tts_router, create_event_router, create_llm_router, create_health_router
from models.llm import Qwen
from models.tts import FacebookMms
from fastapi.middleware.cors import CORSMiddleware
from bucket.objectStorage import ObjectStorage
from database.database import Database
from database.models import ProcessingRiotEventJob
from contextlib import asynccontextmanager

class Server:

    llm_models = None
    tts_models = None
    current_llm: Model = None
    current_tts: Model = None

    def __init__(self) -> None:
        self.bucket = ObjectStorage()
        self.database = Database()
        self.events = Queue[ProcessingRiotEventJob]()

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup: Start background tasks
            await self.startup_event()
            yield
            # Shutdown: cleanup if needed
            print("🔄 Shutting down...")

        self.app = FastAPI(lifespan=lifespan)


        self._init_middleware()
        self._init__models()
        self._init__routes()

    def _init__models(self):
        self.llm_models = {
            "Qwen/Qwen3-0.6B": Qwen(),
            "dphn/Dolphin-X1-8B-GGUF": DolphinGGUF(),
            "dphn/Dolphin3.0-Llama3.1-8B-GGUF-F16": DolphinGGUF("dphn/Dolphin3.0-Llama3.1-8B-GGUF", "Dolphin3.0-Llama3.1-8B-F16.gguf"),
            "dphn/Dolphin3.0-Llama3.1-8B-GGUF-Q8": DolphinGGUF("dphn/Dolphin3.0-Llama3.1-8B-GGUF", "Dolphin3.0-Llama3.1-8B-Q8_0.gguf"),
        }

        self.tts_models = {
            "facebook/mms-tts-fra": FacebookMms(),
            "facebook/mms-tts-eng": FacebookMms("facebook/mms-tts-eng")
        }

        self.current_llm = self.llm_models['Qwen/Qwen3-0.6B']
        self.current_tts =self.tts_models['facebook/mms-tts-fra']
        
        self.current_llm.load()
        self.current_tts.load()

        print(f"🔍 Current LLM: {self.current_llm.model_name}")
        print(f"🔍 Current TTS: {self.current_tts.model_name}")

    def _init_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.app.middleware("http")(add_auth_header)

    def _init__routes(self):
        events_router, self.start_events_processor = create_event_router(
            self.events,
            self.current_tts, 
            self.current_llm,
            self.bucket,
            self.database
        )
        llm_router = create_llm_router(
            self.llm_models,
            get_current_llm=lambda: self.current_llm,
            set_current_llm=lambda model: setattr(self, 'current_llm', model),
            is_queue_empty=lambda: self.events.empty()
        )
        tts_router = create_tts_router(
            self.tts_models,
            get_current_tts=lambda: self.current_tts,
            set_current_tts=lambda model: setattr(self, 'current_tts', model),
            is_queue_empty=lambda: self.events.empty()
        )

        health_router = create_health_router()

        self.app.include_router(events_router, prefix="/events")
        self.app.include_router(llm_router, prefix="/llm")
        self.app.include_router(tts_router, prefix="/tts")
        self.app.include_router(health_router, prefix="/health")

    async def startup_event(self):
        """Called when the server starts (event loop is running)"""
        print("🚀 Server startup - initializing background tasks")
        await self.start_events_processor()      

