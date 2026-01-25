import asyncio
from asyncio.queues import Queue
from pathlib import Path
from typing import Annotated, List
from datetime import datetime

from fastapi import Depends

from externals.objectStorage import ObjectStorage
from database.database import Database
from database.models import ProcessingRiotEventJob, ProcessingRiotEventStatus
from dependencies.state import get_database, get_object_storage, get_events_queue, get_events_status, get_model_registry, get_prompt_manager
from ai.models.registry import ModelRegistry
from ai.prompts.manager import PromptManager


class EventService:
    """Service for managing events"""
    
    def __init__(
        self, 
        model_registry: Annotated[ModelRegistry, Depends(get_model_registry)],
        events_queue: Annotated[Queue[ProcessingRiotEventJob], Depends(get_events_queue)],
        events_status: Annotated[Queue[ProcessingRiotEventJob], Depends(get_events_status)],
        prompt_manager: Annotated[PromptManager, Depends(get_prompt_manager)],
        database: Annotated[Database, Depends(get_database)],
        object_storage: Annotated[ObjectStorage, Depends(get_object_storage)]
    ):
        self._model_registry = model_registry
        self._events_queue = events_queue
        self._events_status = events_status
        self._prompts_manager = prompt_manager

        self._bucket = object_storage
        self._database = database 

        self._tracked_events = dict[str, ProcessingRiotEventJob]()

    async def add_events(self, events_ids: List[str]) -> List[str]:
        """Add events to the queue"""

        result = []

        for id in events_ids:

            riot_event = self._database.get_riot_event_by_id(id)
            if riot_event is None:
                raise ValueError(f"Riot event id {id} not found")

            prompt = self._prompts_manager.get_prompt(riot_event.eventName, riot_event.eventData)

            processing_riot_event_job = ProcessingRiotEventJob(
                riot_event_id=id,
                status=ProcessingRiotEventStatus.PENDING,
                input_text=prompt
            )

            await self._events_queue.put(processing_riot_event_job)
            await self._events_status.put(processing_riot_event_job)

            self._tracked_events[processing_riot_event_job.id] = processing_riot_event_job

            self._database.save_processing_riot_event_job(processing_riot_event_job)
        
            result.append(processing_riot_event_job.id)

        return result

    async def get_last_events_status(self):
        return await self._events_status.get()

    def get_tracked_events_values(self):
        """Get all tracked events"""
        return list(self._tracked_events.values())

    async def clear_events(self):
        """Clear all events"""
        sizes = (len(self._tracked_events), self._events_queue.qsize(), self._events_status.qsize()) 
        
        self._tracked_events.clear()
        
        while not self._events_queue.empty():
            self._events_queue.get_nowait()

        while not self._events_status.empty():
            self._events_status.get_nowait()

        return sizes

    async def events_processor(self):
        """Task that processes events"""        
        while True:

            last_event = await self._events_queue.get()

            print(f"🤖 Processing event id {last_event.id}")

            last_event.status = ProcessingRiotEventStatus.PROCESSING
            self._database.update_processing_riot_events_job(last_event)
            await self._events_status.put(last_event)

            current_llm = self._model_registry.current_llm
            last_event.llm_started_at = datetime.now()
            last_event.llm_model_name = current_llm.model_name

            response = await asyncio.to_thread(current_llm.generate, self._prompts_manager.get_system_prompt(), last_event.input_text)

            last_event.llm_completed_at = datetime.now()
            last_event.llm_text = response['answer']

            print(f"📝 Raw response LLM {response['answer'][:25]}...")

            current_tts = self._model_registry.current_tts
            last_event.tts_started_at = datetime.now()
            last_event.tts_model_name = current_tts.model_name
            audio_path,audio_duration = await asyncio.to_thread(current_tts.generate, response['answer'])

            last_event.tts_completed_at = datetime.now()

            print(f"🔊 Audio path bucket {audio_path}")

            audio_url = self._bucket.upload(audio_path)

            last_event.audio_url = audio_url
            last_event.audio_duration = audio_duration

            self._tracked_events.pop(last_event.id)

            last_event.status = ProcessingRiotEventStatus.COMPLETED

            self._database.update_processing_riot_events_job(last_event)

            print(f"🔍 Event completed: {last_event.id}")

            await self._events_status.put(last_event)

    async def start_background_tasks(self):
        """This will be called when the server starts"""
        asyncio.create_task(self.events_processor())
        print("✅ Background event processor task created") 