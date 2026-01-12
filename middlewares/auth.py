from fastapi import HTTPException, Request
from os import getenv
from dotenv import load_dotenv

load_dotenv()

_token = getenv("AUTH_TOKEN")

if not _token:
    raise ValueError('Require TOKEN as env variable')

async def verify_token_flexible(request: Request):
    """Dependency that checks both query param and Authorization header"""
    token = request.query_params.get("token")
    
    if token and token == _token:
        return True
    
    auth_header = request.headers.get("Authorization")
    if auth_header != f"Bearer {_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return True