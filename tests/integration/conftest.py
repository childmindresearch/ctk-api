"""Fixtures and configurations for testing the endpoints of the CTK API."""
import enum

import pytest
from fastapi import testclient
from pytest_mock import plugin

from ctk_api import main

API_ROOT = "/api/v1"


class Endpoints(str, enum.Enum):
    """Enum class that represents the available endpoints for the API."""

    ANONYMIZE_REPORT = f"{API_ROOT}/summarization/anonymize_report"
    SUMMARIZE_REPORT = f"{API_ROOT}/summarization/summarize_report"
    GET_DIAGNOSES = f"{API_ROOT}/diagnoses"
    POST_DIAGNOSIS = f"{API_ROOT}/diagnoses"  # noqa: PIE796
    PATCH_DIAGNOSIS = f"{API_ROOT}/diagnoses/{{diagnosis_id}}"
    DELETE_DIAGNOSIS = f"{API_ROOT}/diagnoses/{{diagnosis_id}}"  # noqa: PIE796
    POST_MARKDOWN_TO_DOCX = f"{API_ROOT}/file_conversion/md2docx"


@pytest.fixture()
def endpoints() -> type[Endpoints]:
    """Returns the Endpoints enum class."""
    return Endpoints


@pytest.fixture()
def client(mocker: plugin.MockerFixture) -> testclient.TestClient:
    """Returns a test client for the API."""
    return testclient.TestClient(main.app)
