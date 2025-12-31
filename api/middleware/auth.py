from fastapi import Response, Request
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("AUTH_TOKEN")

if not TOKEN:
    raise ValueError("AUTH_TOKEN is not set")

async def add_auth_header(request: Request, call_next):

    token = request.query_params.get("token")
    
    if token != None and token == TOKEN:
        return await call_next(request)


    if request.headers.get("Authorization") != f"Bearer {TOKEN}":
        return Response(status_code=401, content="Unauthorized")

    return await call_next(request)