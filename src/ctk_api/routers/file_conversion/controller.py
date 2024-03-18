"""View definitions for the file conversion router."""

import logging
import tempfile

import fastapi
from fastapi import responses, status

from ctk_api.core import config, core_utils
from ctk_api.routers.file_conversion.intake import parser, writer
from ctk_api.routers.file_conversion.intake import utils as intake_utils

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
    return core_utils.markdown_text_as_docx_response(
        markdown_text,
        background_tasks,
        status_code=status.HTTP_200_OK,
    )


def intake_to_docx(
    csv_file: fastapi.UploadFile,
    redcap_survery_identifier: int,
    background_tasks: fastapi.BackgroundTasks,
) -> responses.FileResponse:
    """Converts an intake CSV file to a docx file.

    Args:
        csv_file: The intake CSV file.
        redcap_survery_identifier: The REDCap survey identifier for the intake form.
        background_tasks: The FastAPI background tasks object.

    Returns:
        The response with the docx file.
    """
    subject_df = intake_utils.read_subject_row(csv_file, redcap_survery_identifier)
    intake_info = parser.IntakeInformation(subject_df.row(0, named=True))
    report_writer = writer.ReportWriter(intake_info)
    report_writer.transform()
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as docx_file:
        report_writer.report.save(docx_file.name)

    background_tasks.add_task(core_utils.remove_file, docx_file.name)
    return responses.FileResponse(
        docx_file.name,
        filename="report.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks,
        status_code=status.HTTP_200_OK,
    )
