from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Body
from typing import Dict, List
import asyncio


@asynccontextmanager
async def overlay_router_lifespan(app: FastAPI):
    print("Overlay router lifespan started")
    try:
        yield
    finally:
        print("Overlay router shutdown complete")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.control_panel_state: Dict[str, Dict] = {
            "particleCount": 50,
            "particleSpeed": 0.8,
            "baseSize": 15,
            "baseHue": 180,
            "numberOfStars": 3,
            "blackParticles": False,
            "blackStars": False,
            "trailLength": 5,
            "rotationSpeed": 0.03,
            "starSpeed": 0.02,
            "starSize": 0.2,
            "starOffset": 1.02,
            "wanderStrength": 0.1,
            "collisionForce": 0.5,
            "trailColor": 0
        }

    async def connect(self, websocket: WebSocket):
        client_connection = await websocket.receive_json()
        self.active_connections[client_connection["client"]] = websocket
        if client_connection["client"] == "overlay":
            await self.broadcast_to_overlays()

    def disconnect(self, websocket: WebSocket):
        # Find and remove the client key associated with this websocket
        for client, ws in list(self.active_connections.items()):
            if ws == websocket:
                del self.active_connections[client]
                break

    async def send_message(self, message: str, client: str):
        if client in self.active_connections:
            await self.active_connections[client].send_text(message)

    async def disconnect_all(self):
        for client, connection in list(self.active_connections.items()):
            await connection.close()
            del self.active_connections[client]

    async def broadcast_to_overlays(self):
        while True:
            await asyncio.sleep(0.5)
            if "overlay" in self.active_connections.keys():
                await self.active_connections["overlay"].send_json(self.control_panel_state)


overlay_router = APIRouter(lifespan=overlay_router_lifespan)
manager = ConnectionManager()


@overlay_router.websocket("/overlay")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                # print(data)
                if data.get("client") == "control_panel":
                    manager.control_panel_state = data["data"]
                await asyncio.sleep(0.5)
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
