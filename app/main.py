from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import jobs
from app.services.scheduler import start_scheduler
from app.core.database import init_db, engine, Session
from app.core.models import UserPreferences
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LinkedIn Job Agent API")

# Mount Static Files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    
    # Create a default user if none exists
    with Session(engine) as session:
        default_user = session.get(UserPreferences, 1)
        if not default_user:
            logger.info("Creating default user with ID 1...")
            user = UserPreferences(
                id=1,
                email="example@gmail.com",
                keywords="Python,Backend",
                linkedin_search_url="https://www.linkedin.com/jobs/search/?keywords=Python&location=Turkey"
            )
            session.add(user)
            session.commit()

    logger.info("Starting scheduler...")
    start_scheduler()

@app.get("/")
async def root():
    index_path = os.path.join(static_path, "index.html")
    return FileResponse(index_path)

app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
