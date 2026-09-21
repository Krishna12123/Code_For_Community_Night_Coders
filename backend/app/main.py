"""
FastAPI Main Application Entrypoint
Owner: Krishna
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.core.config import settings
from app.api.v1.endpoints import cyclones, risk, actions

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API V1 Routers
app.include_router(cyclones.router, prefix=f"{settings.API_V1_STR}/cyclones", tags=["Cyclones & Geospatial"])
app.include_router(risk.router, prefix=f"{settings.API_V1_STR}/risk", tags=["Risk & Exposure"])
app.include_router(actions.router, prefix=f"{settings.API_V1_STR}/actions", tags=["Actions & SOPs"])


# WebSocket Manager for Live Emergency Alerts
class AlertConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = AlertConnectionManager()


@app.websocket(f"{settings.API_V1_STR}/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial connection verification
        await websocket.send_json({
            "type": "SYSTEM_INFO",
            "message": "Connected to Real-Time Cyclone Alert Broadcast Channel"
        })
        while True:
            data = await websocket.receive_text()
            # Handle incoming ping/pong
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Cyclone Risk Assessment & Action Engine Backend",
        "docs": "/docs",
        "version": "1.0.0"
    }
