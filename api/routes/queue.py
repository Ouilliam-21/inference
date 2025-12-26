from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
from queue import Queue
from models.models import Model
from bucket.objectStorage import ObjectStorage
from pydantic import BaseModel
import uuid
import asyncio


class Event(BaseModel):
    id: str
    event: str
    text: str

def create_event_router(
    events_queue: asyncio.Queue[Event], 
    current_tts: Model, 
    current_llm: Model,
    bucket: ObjectStorage
    ) -> APIRouter:
    events_router = APIRouter()
    tracked_events = []
    
    @events_router.get("/events/add", tags=["events"])
    async def add_event():
        last_event = Event(id=str(uuid.uuid4()), event="some_event", text="comment tu vas ?")
        await events_queue.put(last_event)
        tracked_events.append(last_event)
        return {"status": "event added to events"}
    
    @events_router.get("/events/list", tags=["events"])
    async def list_events():
        return {"events": tracked_events}

    async def event_generator():
        while True:

            last_event = await events_queue.get()

            print(f"🔍 Last event: {last_event}")

            response = current_llm.generate(last_event.text)
            print(f"🔍 Raw LLM response: '{response}'")

            jdecoded = json.loads(response)
            audio = current_tts.generate(jdecoded['answer'])

            print(f"🔍 Audio: {audio}")

            bucket.upload(audio)

            tracked_events[:] = [e for e in tracked_events if e.id != last_event.id]

            yield f"data: Server event {last_event.id}\n\n"
   

    @events_router.get("/events")
    async def stream_events():
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    

    return events_router