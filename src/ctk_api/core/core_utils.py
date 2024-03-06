"""Utility functions for the CTK API."""
import logging
import pathlib
import tempfile

import fastapi
import pypandoc
from fastapi import responses

from ctk_api.core import config

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME)


def markdown_text_as_docx_response(
    markdown_text: str,
    background_tasks: fastapi.BackgroundTasks,
    status_code: int,
) -> responses.FileResponse:
    """Converts markdown text to a docx file.

    Args:
        markdown_text: The markdown text to convert.
        background_tasks: The FastAPI background tasks object.
        status_code: The status code to return.

    Returns:
        The response with the docx file.
    """
    with tempfile.NamedTemporaryFile(
        suffix=".docx",
        delete=False,
    ) as output_file, tempfile.NamedTemporaryFile(suffix=".md") as markdown_file:
        markdown_file.write(markdown_text.encode("utf-8"))
        markdown_file.seek(0)
        pypandoc.convert_file(
            markdown_file.name,
            "docx",
            outputfile=str(output_file.name),
        )

    background_tasks.add_task(remove_file, output_file.name)
    return responses.FileResponse(
        output_file.name,
        filename="md2docx.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks,
        status_code=status_code,
    )


def remove_file(filename: str | pathlib.Path) -> None:
    """Removes a file.

    Args:
        filename: The filename of the file to remove.
    """
    logger.debug("Removing file %s.", filename)
    pathlib.Path(filename).unlink()
