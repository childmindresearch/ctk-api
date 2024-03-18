"""View definitions for the file conversion router."""

import logging

import fastapi
from fastapi import responses

from ctk_api.core import config
from ctk_api.routers.file_conversion import controller

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

router = fastapi.APIRouter(prefix="/file_conversion", tags=["file_conversion"])


@router.post("/md2docx")
async def markdown_to_docx(
    markdown_text: str = fastapi.Form(..., description="The markdown text to convert."),
    background_tasks: fastapi.BackgroundTasks = fastapi.BackgroundTasks(),
) -> responses.FileResponse:
    """POST endpoint for converting markdown to .docx.

    Args:
        markdown_text: The markdown text to convert.
        background_tasks: The FastAPI backgrond tasks object.

    Returns:
        str: The .docx file.

    """
    logger.debug("Converting Markdown to .docx")
    response = controller.markdown_to_docx(markdown_text, background_tasks)
    logger.debug("Converted Markdown to .docx.")
    return response


@router.post("/intake2docx")
async def intake_to_docx(
    csv_file: fastapi.UploadFile,
    redcap_survey_identifier: int = fastapi.Form(
        ...,
        description="The REDCap survey identifier for the intake form.",
    ),
    background_tasks: fastapi.BackgroundTasks = fastapi.BackgroundTasks(),
) -> responses.FileResponse:
    """POST endpoint for converting intake to .docx.

    Args:
        csv_file: The intake CSV file from REDCap.
        redcap_survey_identifier: The REDCap survey identifier for the intake form.
        background_tasks: The FastAPI backgrond tasks object.

    Returns:
        str: The .docx file.

    """
    logger.debug("Converting intake from to .docx")
    response = controller.intake_to_docx(
        csv_file,
        redcap_survey_identifier,
        background_tasks,
    )
    logger.debug("Converted intake from to .docx.")
    return response
