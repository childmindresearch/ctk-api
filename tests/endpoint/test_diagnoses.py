"""Tests the diagnoses endpoints."""
import json
import pathlib

from fastapi import status, testclient

import ctk_api

from . import conftest

module_dir = pathlib.Path(ctk_api.__file__).parent
DIAGNOSES_FILE = module_dir / "data" / "diagnoses.json"


def test_diagnoses_endpoint(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the anonymization endpoint."""
    with open(DIAGNOSES_FILE, "r", encoding="utf-8") as file:
        expected = json.load(file)

    actual = client.get(endpoints.DIAGNOSES)

    assert actual.status_code == status.HTTP_200_OK
    assert actual.json() == expected
