from typing import List
from pydantic import BaseModel

class InfoResponse(BaseModel):
    models: List[str]

class CurrentResponse(BaseModel):
    current_model: str

class SetPayload(BaseModel):
    model_name: str

class SetResponse(BaseModel):
    current_model: str