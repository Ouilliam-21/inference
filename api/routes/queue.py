from typing import List
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import json
from models.models import Model
from bucket.objectStorage import ObjectStorage
from pydantic import BaseModel
import asyncio
from database.models import ProcessingRiotEventJob, ProcessingRiotEventStatus
from database.database import Database
import uuid
from datetime import datetime
from prompts.manager import PromptManager

class EventIds(BaseModel):
    eventIds: List[str]

def create_event_router(
    events_queue: asyncio.Queue[ProcessingRiotEventJob], 
    current_tts: Model, 
    current_llm: Model,
    bucket: ObjectStorage,
    database: Database
    ) -> APIRouter:
    events_router = APIRouter()
    tracked_events = dict[str, ProcessingRiotEventJob]()
    events_status = asyncio.Queue[ProcessingRiotEventJob]()
    prompts_manager = PromptManager("../config.yaml")
    
    @events_router.post("/", tags=["events"])
    async def add_event(event_ids: EventIds):

        for id in event_ids.eventIds:

            riot_event = database.get_riot_event_by_id(id)
            if riot_event is None:
                raise HTTPException(status_code=404, detail="Riot event not found")

            prompt = prompts_manager.get_prompt(riot_event.eventName, riot_event.eventData)

            processing_riot_event_job = ProcessingRiotEventJob(
                riot_event_id=id,
                status=ProcessingRiotEventStatus.PENDING,
                input_text=prompt
            )
            await events_queue.put(processing_riot_event_job)
            await events_status.put(processing_riot_event_job)
            tracked_events[processing_riot_event_job.id] = processing_riot_event_job

            database.save_processing_riot_event_job(processing_riot_event_job)

        return {"status": "event added to events"}
    
    @events_router.get("/list", tags=["events"])
    async def list_events():
        return {"events": list(tracked_events.values())}

    @events_router.get("/clear", tags=["events"])
    async def clear_events():
        tracked_events.clear()
        
        while not events_queue.empty():
            events_queue.get_nowait()

        while not events_status.empty():
            events_status.get_nowait()

        return {"status": "success"}

    async def events_processor():
        """Background task that processes events - runs independently"""
        print("🚀 Starting background event processor")
        
        while True:

            last_event = await events_queue.get()

            print(f"🔍 Last event: {last_event.id}")

            last_event.status = ProcessingRiotEventStatus.PROCESSING
            database.update_processing_riot_events_job(last_event)
            await events_status.put(last_event)

            last_event.llm_started_at = datetime.now()
            last_event.llm_model_name = current_llm.model_name

            response = await asyncio.to_thread(current_llm.generate, prompts_manager.get_system_prompt(), last_event.input_text)

            last_event.llm_completed_at = datetime.now()
            last_event.llm_text = response['answer']

            print(f"🔍 Raw LLM response: '{response['answer']}'")

            last_event.tts_started_at = datetime.now()
            last_event.tts_model_name = current_tts.model_name
            audio_path,audio_duration = await asyncio.to_thread(current_tts.generate, response['answer'])

            last_event.tts_completed_at = datetime.now()

            print(f"🔍 Audio: {audio_path}")

            audio_url = bucket.upload(audio_path)

            last_event.audio_url = audio_url
            last_event.audio_duration = audio_duration

            tracked_events.pop(last_event.id)

            last_event.status = ProcessingRiotEventStatus.COMPLETED

            database.update_processing_riot_events_job(last_event)

            print(f"🔍 Event completed: {last_event.id}")

            await events_status.put(last_event)

    @events_router.get("/sse/status")
    async def stream_events_status(request: Request):
        async def generator():
            while True:
                if await request.is_disconnected():
                    break

                last_event = await events_status.get()
                yield ": keep-alive\n\n"
                yield (
                    f"event: event_status\n"
                    f"id: {uuid.uuid4()}\n"
                    f"retry: 1000\n"
                    f"data: {last_event.model_dump_json()}\n\n"
                )
                await asyncio.sleep(0.25)

        async def generator_testing():

            while True:
                faker = ProcessingRiotEventJob(
                    riot_event_id=f"{uuid.uuid4()}",
                    status=ProcessingRiotEventStatus.PENDING,
                    input_text="test"
                )
                yield ": keep-alive\n\n"
                yield (
                    f"event: event_status\n"
                    f"id: {uuid.uuid4()}\n"
                    f"retry: 1000\n"
                    f"data: {faker.model_dump_json()}\n\n"
                )
                await asyncio.sleep(2)

        return StreamingResponse(
            generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )        
    async def start_background_tasks():
        """This will be called when the server starts"""
        asyncio.create_task(events_processor())
        print("✅ Background event processor task created")    
    
    return events_router, start_background_tasks