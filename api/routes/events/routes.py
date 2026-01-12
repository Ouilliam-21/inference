from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from routes.events.generator import generator
from schemas.events.schema import AddPayload, AddResponse, ClearResponse, InfoResponse
from services.events.service import EventService

Service = Annotated[EventService, Depends()]

events_router = APIRouter(prefix="/events", tags=["events"])

@events_router.post("/add", response_model=AddResponse)
async def add_event(events: AddPayload, service: Service):
    return AddResponse(saved_ids=service.add_events(events.events_ids))

@events_router.get("/list", response_model=InfoResponse)
async def list_events(service: Service):
    """List all events"""
    return InfoResponse(events=service.get_tracked_events_values())

@events_router.put("/clear", response_model=ClearResponse)
async def clear_events(service: Service):
    """Clear all events"""
    tracked, queue, status = service.clear_events()
    return ClearResponse(tracked=tracked, queue=queue, status=status)

@events_router.get("/sse")
async def stream_events_status(request: Request, service: Service):
    return StreamingResponse(
        generator(request, service),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )  