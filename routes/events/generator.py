from asyncio import sleep
from fastapi import Request
from uuid import uuid4
from datetime import datetime, timedelta
from random import uniform

from database.models import ProcessingRiotEventJob, ProcessingRiotEventStatus
from services.events.service import EventService

async def generator(request: Request, service: EventService):
    while True:
        if await request.is_disconnected():
            break

        last_event = await service.get_last_events_status()
        yield ": keep-alive\n\n"
        yield (
            f"event: event_status\n"
            f"id: {uuid4()}\n"
            f"retry: 1000\n"
            f"data: {last_event.model_dump_json()}\n\n"
        )
        await sleep(0.25)

async def generator_testing(request: Request, service: EventService):

    while True:
        faker = ProcessingRiotEventJob(
            riot_event_id=f"{uuid4()}",
            status=ProcessingRiotEventStatus.PENDING,
            input_text="Fake test input"
        )
        yield ": keep-alive\n\n"
        yield (
            f"event: event_status\n"
            f"id: {uuid4()}\n"
            f"retry: 1000\n"
            f"data: {faker.model_dump_json()}\n\n"
        )
        await sleep(5)

        faker.status=ProcessingRiotEventStatus.PROCESSING

        yield ": keep-alive\n\n"
        yield (
            f"event: event_status\n"
            f"id: {uuid4()}\n"
            f"retry: 1000\n"
            f"data: {faker.model_dump_json()}\n\n"
        )
        await sleep(5)

        faker.status=ProcessingRiotEventStatus.COMPLETED
        faker.audio_url="https://ouilliam-audio.nyc3.digitaloceanspaces.com/tts_output_f4ae88ab-cc37-4e41-a18a-c967cbe2160b.wav"

        faker.llm_started_at = datetime.now() - timedelta(seconds=15)
        faker.llm_completed_at = datetime.now() - timedelta(seconds=14)
        faker.llm_model_name = "fake-llm"
        faker.llm_text = "Voici une réponse LLM de test vulgaire."
        faker.error_message = None
        faker.tts_started_at = datetime.now() - timedelta(seconds=12)
        faker.tts_completed_at = datetime.now() - timedelta(seconds=10)
        faker.tts_model_name = "fake-tts"
        faker.audio_duration = uniform(2.5, 8.0)
        faker.created_at = datetime.now() - timedelta(seconds=20)
        faker.updated_at = datetime.now()



        yield ": keep-alive\n\n"
        yield (
            f"event: event_status\n"
            f"id: {uuid4()}\n"
            f"retry: 1000\n"
            f"data: {faker.model_dump_json()}\n\n"
        )

        await sleep(5)
