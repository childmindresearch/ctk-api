"""View definitions for the file conversion router."""
import logging
import tempfile

import fastapi
import polars as pl
from fastapi import responses, status

from ctk_api.core import config, utils
from ctk_api.routers.file_conversion.intake import parser, writer

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
        status_code=status.HTTP_200_OK,
    )


def intake_to_docx(
    csv_file: fastapi.UploadFile,
    first_name: str,
    last_name: str,
    background_tasks: fastapi.BackgroundTasks,
) -> responses.FileResponse:
    """Converts an intake CSV file to a docx file.

    Args:
        csv_file: The intake CSV file.
        first_name: The first name of the subject.
        last_name: The last name of the subject.
        background_tasks: The FastAPI background tasks object.

    Returns:
        The response with the docx file.
    """
    subject_df = _read_subject_row(csv_file, first_name, last_name)
    intake_info = parser.IntakeInformation(subject_df.row(0, named=True))
    report_writer = writer.ReportWriter(intake_info)
    report_writer.transform()
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as docx_file:
        report_writer.report.save(docx_file.name)

    background_tasks.add_task(utils.remove_file, docx_file.name)
    return responses.FileResponse(
        docx_file.name,
        filename="report.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks,
        status_code=status.HTTP_200_OK,
    )


def _read_subject_row(
    csv_file: fastapi.UploadFile,
    first_name: str,
    last_name: str,
) -> pl.DataFrame:
    """Reads the subject row from the intake CSV file.

    Args:
        csv_file: The intake CSV file.
        first_name: The first name of the subject.
        last_name: The last name of the subject.

    Returns:
        The subject row.

    Raises:
        HTTPException: If the subject is not found.
    """
    intake_df = pl.read_csv(csv_file.file)
    subject_df = intake_df.filter(
        (intake_df["firstname"] == first_name) & (intake_df["lastname"] == last_name),
    )
    if subject_df.height == 1:
        return subject_df

    if subject_df.height > 1:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Multiple subjects found.",
        )

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Subject not found.",
    )
