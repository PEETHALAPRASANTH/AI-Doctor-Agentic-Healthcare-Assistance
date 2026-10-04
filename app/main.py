from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import get_settings
from .database import init_db
from .api.routes import router


settings = get_settings()

app = FastAPI(
    title="AI Doctor Agent",
    version="1.0.0",
    description=(
        "Educational Agentic AI healthcare information assistant. "
        "Not a diagnostic system."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(router)


@app.on_event("startup")
def startup():
    init_db()


BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "dist"


@app.get("/{full_path:path}")
async def serve_react(full_path: str):

    file_path = DIST_DIR / full_path

    if file_path.is_file():
        return FileResponse(file_path)
 
    return FileResponse(DIST_DIR / "index.html")