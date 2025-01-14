from fastapi import APIRouter
from .audio_player import audio_player_router
from .overlays import overlay_router

ws_router = APIRouter()

ws_router.include_router(audio_player_router)
ws_router.include_router(overlay_router)
