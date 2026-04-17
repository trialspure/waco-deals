import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import properties, offers, admin, settings as settings_router
from app.routes import analysis
from app.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (Alembic handles migrations in production)
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    logger.info("Waco Deals backend started")
    yield
    stop_scheduler()


app = FastAPI(
    title="Waco Real Estate Deal Finder",
    description="Automatically scrape, score, and generate offers for Waco, TX investment properties.",
    version="1.0.0",
    lifespan=lifespan,
)

import os
_FRONTEND_URL = os.getenv("FRONTEND_URL", "")
_ALLOWED_ORIGINS = list(filter(None, [
    _FRONTEND_URL,
    "https://waco-deals-frontend.onrender.com",
    "http://localhost:3000",
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties.router)
app.include_router(offers.router)
app.include_router(admin.router)
app.include_router(settings_router.router)
app.include_router(analysis.router)


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"status": "ok", "app": "Waco Real Estate Deal Finder"}
