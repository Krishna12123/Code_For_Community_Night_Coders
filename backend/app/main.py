"""
FastAPI Main Application Entrypoint
Owner: Krishna
"""

from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db
from app.routers import cyclones, risk, actions, geospatial
from app.schemas.models import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler for startup and shutdown operations.
    Initializes database tables and seeds initial spatial data.
    """
    print("[Backend Startup] Initializing Database & Seed Records...")
    init_db()
    print("[Backend Startup] Database Ready.")
    yield
    print("[Backend Shutdown] Shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(cyclones.router, prefix=f"{settings.API_V1_STR}/cyclones", tags=["Cyclones & Tracking"])
app.include_router(risk.router, prefix=f"{settings.API_V1_STR}/risk", tags=["Risk & Exposure"])
app.include_router(actions.router, prefix=f"{settings.API_V1_STR}/actions", tags=["Actions & SOPs"])
app.include_router(geospatial.router, prefix=f"{settings.API_V1_STR}/geospatial", tags=["Geospatial & GEE Layers"])


# WebSocket Manager for Live Emergency Alerts
class AlertConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = AlertConnectionManager()


@app.websocket(f"{settings.API_V1_STR}/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial connection verification
        await websocket.send_json({
            "type": "SYSTEM_INFO",
            "message": "Connected to Real-Time Cyclone Alert Broadcast Channel",
            "active_cyclone": "CYC-2026-01"
        })
        while True:
            data = await websocket.receive_text()
            # Echo or broadcast if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="online",
        service="Cyclone Risk Assessment & Action Engine Backend",
        docs="/docs",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="Cyclone Risk Assessment & Action Engine Backend",
        docs="/docs",
        version="1.0.0"
    )
