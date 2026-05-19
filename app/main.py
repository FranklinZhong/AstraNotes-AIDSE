"""AstraNotes API — main application entry point."""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import auth, notes

app = FastAPI(title="AstraNotes API", version="1.0.0")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "AstraNotes API", "version": "1.0.0"}


# Serve web UI — mount static files if directory exists
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_ui():
        return FileResponse(os.path.join(_static_dir, "index.html"))
