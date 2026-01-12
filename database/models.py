from enum import Enum
from typing import Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field

class ProcessingRiotEventStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingRiotEventJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    riot_event_id: str
    status: ProcessingRiotEventStatus
    input_text: str
    llm_started_at: Optional[datetime] = None
    llm_completed_at: Optional[datetime] = None
    llm_model_name: Optional[str] = None
    llm_text: Optional[str] = None
    error_message: Optional[str] = None
    tts_started_at: Optional[datetime] = None
    tts_completed_at: Optional[datetime] = None
    tts_model_name: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    class Config:
        arbitrary_types_allowed = True

class RiotEvent():
    id: str
    gameSessionId: str
    riotEventId: int
    eventName: str
    eventData: dict
    createdAt: datetime
    
    def __init__(self, id: str, gameSessionId: str, riotEventId: int, eventName: str, eventData: dict, createdAt: datetime):
        self.id = id
        self.gameSessionId = gameSessionId
        self.riotEventId = riotEventId
        self.eventName = eventName
        self.eventData = eventData
        self.createdAt = createdAt