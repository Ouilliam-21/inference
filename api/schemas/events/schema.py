from typing import List
from pydantic import BaseModel, Field

from database.models import ProcessingRiotEventJob

class AddPayload(BaseModel):
    events_ids: List[str]

class AddResponse(BaseModel):
    saved_ids: List[str]

class InfoResponse(BaseModel):
    events: List[ProcessingRiotEventJob]

class ClearResponse(BaseModel):
    tracked: int
    queue: int
    status: int