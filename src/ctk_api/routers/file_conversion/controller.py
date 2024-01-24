"""View definitions for the file conversion router."""
import logging

import fastapi
from fastapi import responses

from ctk_api.core import config, utils

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def markdown_to_docx(
    markdown_text: str,
    background_tasks: fastapi.BackgroundTasks,
) -> responses.FileResponse:
    """Converts markdown text to a docx file.

    Args:
        markdown_text: The markdown text to convert.
        background_tasks: The FastAPI background tasks object.

    Returns:
        The response with the docx file.
    """
    return utils.markdown_text_as_docx_response(
        markdown_text,
        background_tasks,
        status_code=200,
    )
