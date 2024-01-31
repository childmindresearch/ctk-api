"""Configurations for all tests."""
import tempfile
from collections.abc import Generator

import docx
import pytest
from sqlalchemy import orm

from ctk_api.core import config
from ctk_api.microservices import sql

settings = config.get_settings()
ENVIRONMENT = settings.ENVIRONMENT


@pytest.fixture(autouse=True)
def _reset_testing_db() -> None:
    """Resets the testing database."""
    database = sql.Database()
    if (
        database.get_db_url() != "sqlite:///tests/test.sqlite"
        and ENVIRONMENT != "ci-testing"
    ):
        msg = "Testing database is not configured correctly."
        raise ValueError(msg)
    sql.Base.metadata.drop_all(database.engine)
    database.create_database_schema()


@pytest.fixture()
def session() -> orm.Session:
    """Gets a database session."""
    return next(sql.get_session())


@pytest.fixture()
def document() -> Generator[tempfile._TemporaryFileWrapper, None, None]:
    """Generates a fixture Word document.

    This document contains a title and a paragraph.

    Returns:
        Generator[tempfile._TemporaryFileWrapper, None, None]: The saved file.
    """
    doc = docx.Document()
    doc.add_heading("Title", 0)
    doc.add_heading("clinical summary and impressions", 1)
    doc.add_paragraph("Name: Lea Avatar")
    doc.add_paragraph("He she herself man")
    doc.add_heading("recommendations", 1)
    doc.add_paragraph("hello!")

    with tempfile.NamedTemporaryFile(suffix=".docx") as temp_file:
        doc.save(temp_file.name)
        yield temp_file
