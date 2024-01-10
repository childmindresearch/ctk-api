"""The controller for the summarization router."""
import functools
import logging
import pathlib
import tempfile
from typing import Literal

import docx
import fastapi
import openai
import pypandoc
import yaml
from fastapi import responses, status
from sqlalchemy import orm

from ctk_api.core import config
from ctk_api.routers.summarization import anonymizer, models, schemas

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME
OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_CHAT_COMPLETION_MODEL = settings.OPENAI_CHAT_COMPLETION_MODEL
OPENAI_CHAT_COMPLETION_PROMPT_FILE = settings.OPENAI_CHAT_COMPLETION_PROMPT_FILE

logger = logging.getLogger(LOGGER_NAME)


def anonymize_report(docx_file: fastapi.UploadFile) -> str:
    """Anonymizes a clinical report.

    Args:
        docx_file: The report's docx file to anonymize.

    Returns:
        str: The anonymized file.

    Notes:
        This function is specific to the file format used by HBN's clinical
        reports and will not work for other file formats.
    """
    logger.info("Anonymizing report.")
    document = docx.Document(docx_file.file)
    first_name, last_name = anonymizer.get_patient_name(document)
    paragraphs = anonymizer.get_diagnostic_paragraphs(document)
    anonymized_paragraphs = anonymizer.anonymize_paragraphs(
        paragraphs,
        first_name,
        last_name,
    )
    return "\n".join([p.text for p in anonymized_paragraphs])


async def summarize_report(
    report: schemas.Report,
    session: orm.Session,
    background_tasks: fastapi.BackgroundTasks,
) -> responses.FileResponse:
    """Summarizes a clinical report.

    Clinical reports are sent to OpenAI. Both the report and the summary are
    stored in the database.

    Args:
        report: The report to summarize.
        session: The database session.
        background_tasks: The background tasks to run.

    Returns:
        str: The summarized file.
    """
    logger.info("Checking if request was made before.")
    existing_document = (
        session.query(models.Summary)
        .filter(
            models.Summary.anonymous_text == report.text,
        )
        .first()
    )

    if existing_document:
        return _summmary_as_docx_response(
            existing_document.summary_text,
            background_tasks,
            status.HTTP_200_OK,
        )

    system_prompt = get_prompt("system", "summarize_clinical_report")

    logger.debug("Sending report to OpenAI.")
    client = openai.OpenAI(api_key=OPENAI_API_KEY.get_secret_value())
    response = client.chat.completions.create(
        model=OPENAI_CHAT_COMPLETION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": report.text},
        ],
    )

    logger.debug("Saving response from OpenAI.")
    response_text = response.choices[0].message.content

    if response_text is None:
        logger.error("No response was received from OpenAI.")
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No response was received from OpenAI.",
        )

    summary = models.Summary(
        anonymous_text=report.text,
        summary_text=response_text,
    )
    session.add(summary)
    session.commit()

    return _summmary_as_docx_response(
        response_text,
        background_tasks,
        status.HTTP_201_CREATED,
    )


@functools.lru_cache
def get_prompt(category: Literal["system", "user"], name: str) -> str:
    """Gets the system prompt for the OpenAI chat completion model.

    Args:
        category: The type of prompt to get.
        name: The name of the prompt to get.

    Returns:
        str: The system prompt.
    """
    logger.debug("Getting %s prompt: %s.", category, name)
    with OPENAI_CHAT_COMPLETION_PROMPT_FILE.open("r") as file:
        prompts = yaml.safe_load(file)
    return prompts[category][name]


def _remove_file(filename: str | pathlib.Path) -> None:
    """Removes a file.

    Args:
        filename: The filename of the file to remove.
    """
    logger.debug("Removing file %s.", filename)
    pathlib.Path(filename).unlink()


def _summmary_as_docx_response(
    markdown_text: str,
    background_tasks: fastapi.BackgroundTasks,
    status_code: int,
) -> responses.FileResponse:
    """Converts markdown text to a docx file.

    Args:
        markdown_text: The markdown text to convert.
        background_tasks: The background tasks to run.
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

    background_tasks.add_task(_remove_file, output_file.name)
    return responses.FileResponse(
        output_file.name,
        filename="summary.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        background=background_tasks,
        status_code=status_code,
    )
