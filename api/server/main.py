from asyncio import Queue
from fastapi import FastAPI
from models.models import Model
from routes.llm import create_llm_router
from routes.queue import create_event_router
from routes.tts import create_tts_router
from models.llm import Qwen
from models.tts import FacebookMms
from fastapi.middleware.cors import CORSMiddleware
from bucket.objectStorage import ObjectStorage

class Server:

    llm_models = None
    tts_models = None
    current_llm: Model = None
    current_tts: Model = None
    events: Queue = None

    def __init__(self) -> None:
        self.app = FastAPI()
        self.bucket = ObjectStorage()
        self.events = Queue()

        self._init_middleware()
        self._init__models()
        self._init__routes()

    def _init__models(self):
        self.llm_models = {
            "Qwen/Qwen3-0.6B": Qwen()
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


    def _init__routes(self):
        events_router = create_event_router(
            self.events,
            self.current_tts, 
            self.current_llm,
            self.bucket
        )
        llm_router = create_llm_router(
            self.llm_models,
            get_current_llm=lambda: self.current_llm,
            set_current_llm=lambda model: setattr(self, 'current_llm', model)
            )
        tts_router = create_tts_router(
            self.tts_models,
            get_current_tts=lambda: self.current_tts,
            set_current_tts=lambda model: setattr(self, 'current_tts', model)
        )

        self.app.include_router(events_router)
        self.app.include_router(llm_router)
        self.app.include_router(tts_router)

