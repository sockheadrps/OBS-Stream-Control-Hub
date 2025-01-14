import json
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from .api.genfuel import FuelEstimator
from .db.db_manager import DatabaseManager
from .api.report import get_report_data, generate_zip_reports, generate_csv_reports, generate_excel_reports
import uvicorn
import os
from contextlib import asynccontextmanager
import pandas as pd
from pathlib import Path
import zipfile
import io
from .config.generator_list import generators, generator_fuel_capacity
from .websockets.endpoints import ws_router as websocket_router
import signal
import sys

def handle_sigint(signal, frame):
    print("\nShutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

load_dotenv()
# load as int
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
FRONTEND_URL = os.getenv("FRONTEND_URL")
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT"))
data_store = {}  # store the data for the fuel est
MUSIC_DIR = os.getenv("MUSIC_DIR")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and clean up resources."""
    db.init_db()
    yield


base_dir = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(lifespan=lifespan)

static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="websockets_static")
app.mount("/templates", StaticFiles(directory=str(templates_dir)), name="websockets_templates")



# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{FRONTEND_URL}:{FRONTEND_PORT}", f"{FRONTEND_URL}:{5174}", f"{FRONTEND_URL}:{8100}"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


app.include_router(websocket_router, prefix="/websockets")

# Database instance
db = DatabaseManager()




@app.get("/music")
async def get_music() -> JSONResponse:
    accepted_types = ["mp3", "wav", "mp4"]
    audio_files = [audio_file for audio_file in os.listdir(MUSIC_DIR) if audio_file.endswith(tuple(accepted_types))]
    resp = {"event": "query_response", "data": audio_files}
    return JSONResponse(content=resp)

if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run("app.main:app", host=SERVER_IP, port=SERVER_PORT)
    except KeyboardInterrupt:
        print("\nServer stopped manually using Ctrl+C.")