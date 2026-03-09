"""
NXFRAME STUDIO — FastAPI Backend
Run: uvicorn api.main:app --reload --port 8000
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from api.config import settings
from api.database import init_db
from api.routers import auth_router, projects_router, contact_router, updates_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    await init_db()
    # Auto-seed on first run
    try:
        from api.seed import seed
        await seed()
    except Exception as e:
        print(f"Seed skipped: {e}")
    print(f"\n{'━'*46}")
    print(f"  NXFRAME STUDIO API — Online")
    print(f"  Docs: http://localhost:{settings.APP_PORT}/docs")
    print(f"{'━'*46}\n")
    yield

app = FastAPI(
    title="NXFRAME STUDIO API",
    description="Portfolio backend for HC Savin",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="api/static"), name="static")

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(contact_router)
app.include_router(updates_router)

@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "service": "NXFRAME STUDIO API", "owner": "HC Savin"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_error(request: Request, exc: Exception):
    print(f"❌ {request.url}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
