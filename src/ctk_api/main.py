"""Main entrypoint for the API."""
import contextlib
import logging
from collections.abc import AsyncGenerator

import fastapi
from fastapi.middleware import cors

from ctk_api.core import config, middleware
from ctk_api.microservices import sql
from ctk_api.routers.diagnoses import views as diagnoses_views
from ctk_api.routers.summarization import views as summarization_views

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

config.initialize_logger()
logger = logging.getLogger(LOGGER_NAME)


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Runs the lifespan events for the API."""
    logger.info("Running startup events.")
    logger.debug("Initializing SQL microservice.")
    database = sql.Database()
    database.create_database_schema()
    sql.create_dev_data()
    yield


logger.info("Initializing API routes.")
api_router = fastapi.APIRouter(prefix="/api/v1")
api_router.include_router(diagnoses_views.router)
api_router.include_router(summarization_views.router)

logger.info("Starting API.")
app = fastapi.FastAPI(
    title="Clinician Toolkit API",
    description="API for the Clinician Toolkit.",
    version="0.1.0",
    contact={
        "name": "Center for Data Analytics, Innovation, and Rigor",
        "url": "https://github.com/childmindresearch/",
        "email": "dair@childmind.org",
    },
    swagger_ui_parameters={"operationsSorter": "method"},
    lifespan=lifespan,
)
app.include_router(api_router)

logger.info("Adding middleware.")
logger.debug("Adding CORS middleware.")
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug("Adding request logger middleware.")
app.add_middleware(middleware.RequestLoggerMiddleware)
