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
    subject_df = _read_subject_row(csv_file, redcap_survery_identifier)
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
    redcap_survey_identifier: int,
) -> pl.DataFrame:
    """Reads the subject row from the intake CSV file.

    All variables are interpreted as strings unless explicitly specified otherwise as
    the REDCap .csv is too inconsistent in its typing.

    Args:
        csv_file: The intake CSV file.
        redcap_survey_identifier: The REDCap survey identifier for the intake form.

    Returns:
        The subject row.

    Raises:
        HTTPException: If the subject is not found.
    """
    dtypes = {
        "age": pl.Float32,
        "birth_location": pl.Int8,
        "child_language1_fluency": pl.Int8,
        "child_language2_fluency": pl.Int8,
        "child_language3_fluency": pl.Int8,
        "childgender": pl.Int8,
        "dominant_hand": pl.Int8,
        "guardian_maritalstatus": pl.Int8,
        "iep": pl.Int8,
        "infanttemp_adapt": pl.Int8,
        "infanttemp1": pl.Int8,
        "language_spoken": pl.Int8,
        "opt_delivery": pl.Int8,
        "residing_number": pl.Int8,
        "pronouns": pl.Int8,
        "schooltype": pl.Int8,
    }

    faulty_people_in_home = 2
    for index in range(1, 11):
        dtypes[f"peopleinhome{index}_relation"] = pl.Int8
        if index != faulty_people_in_home:
            dtypes[f"peopleinhome{index}_relationship"] = pl.Int8
        else:
            dtypes["peopleinhome_relationship"] = pl.Int8

    intake_df = pl.read_csv(
        csv_file.file,
        infer_schema_length=0,
        dtypes=dtypes,
    )

    subject_df = intake_df.filter(
        intake_df["redcap_survey_identifier"] == redcap_survey_identifier,
    )
    if subject_df.height == 1:
        return subject_df

    if subject_df.height > 1:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Multiple patients found.",
        )

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Patient not found.",
    )
