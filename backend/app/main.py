import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import properties, offers, admin, settings as settings_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties.router)
app.include_router(offers.router)
app.include_router(admin.router)
app.include_router(settings_router.router)


@app.get("/")
def root():
    return {"status": "ok", "app": "Waco Real Estate Deal Finder"}
