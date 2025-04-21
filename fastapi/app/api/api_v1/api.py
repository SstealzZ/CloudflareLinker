from fastapi import APIRouter

from .endpoints import auth, dns, logs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dns.router, prefix="/dns", tags=["dns"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"]) 