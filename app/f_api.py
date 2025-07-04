from contextlib import asynccontextmanager
from app.config.logger_config import config_logger
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        config_logger.info("🚀App is starting up...")
        yield
    except Exception as e:
        config_logger.exception(f"❌ Error in the startup stage: {e}")
    finally:
        config_logger.info("👋App shuting down")


f_api = FastAPI(
    title="Parking Lot Management System",
    description="A role-based parking lot system built with FastAPI.",
    version="1.0.0",
    lifespan=lifespan,
)
