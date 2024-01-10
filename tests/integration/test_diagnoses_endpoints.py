"""Tests the diagnoses endpoints."""
import pytest
from fastapi import status, testclient
from sqlalchemy import orm

from ctk_api.routers.diagnoses import models

from . import conftest


@pytest.mark.asyncio()
async def test_get_diagnoses_endpoint(
    client: testclient.TestClient,
    endpoints: conftest.Endpoints,
) -> None:
    """Tests the anonymization endpoint."""
    diagnosis = {"text": "test_text", "children": []}
    client.post(endpoints.POST_DIAGNOSIS, json={"diagnosis": diagnosis})

    response = client.get(endpoints.GET_DIAGNOSES)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["text"] == diagnosis["text"]


@pytest.mark.asyncio()
async def test_create_diagnosis_node_root(
    endpoints: conftest.Endpoints,
    client: testclient.TestClient,
) -> None:
    """Tests creating a root diagnosis."""
    diagnosis = {"text": "test_text_parent"}

    response = client.post(endpoints.POST_DIAGNOSIS, json={"diagnosis": diagnosis})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["text"] == diagnosis["text"]


@pytest.mark.asyncio()
async def test_create_diagnosis_node_child(
    endpoints: conftest.Endpoints,
    client: testclient.TestClient,
) -> None:
    """Tests creating a child diagnosis."""
    diagnosis_parent = {"text": "test_text_parent", "children": []}
    response_parent = client.post(
        endpoints.POST_DIAGNOSIS,
        json={"diagnosis": diagnosis_parent},
    )
    diagnosis_child = {"text": "test_text_child", "children": []}

    response_child = client.post(
        endpoints.POST_DIAGNOSIS,
        json={"diagnosis": diagnosis_child, "parent_id": response_parent.json()["id"]},
    )

    assert response_child.status_code == status.HTTP_201_CREATED
    assert response_child.json()["text"] == diagnosis_child["text"]
    assert response_child.json()["parent_id"] == response_parent.json()["id"]


@pytest.mark.asyncio()
async def test_create_diagnosis_node_multiple(
    endpoints: conftest.Endpoints,
    client: testclient.TestClient,
) -> None:
    """Tests creating multiple nodes."""
    diagnoses = {
        "text": "test_text_parent",
        "children": [
            {"text": "test_text_child_1", "children": []},
            {"text": "test_text_child_2", "children": []},
        ],
    }

    response = client.post(
        endpoints.POST_DIAGNOSIS,
        json={"diagnosis": diagnoses},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["text"] == diagnoses["text"]
    assert len(response.json()["children"]) == len(diagnoses["children"])
    assert response.json()["id"] == response.json()["children"][0]["parent_id"]


@pytest.mark.asyncio()
async def test_patch_diagnosis_node(
    endpoints: conftest.Endpoints,
    client: testclient.TestClient,
) -> None:
    """Tests patching a diagnosis."""
    diagnosis = {"text": "test_text", "children": []}
    response_post = client.post(endpoints.POST_DIAGNOSIS, json={"diagnosis": diagnosis})

    response = client.patch(
        endpoints.PATCH_DIAGNOSIS.format(
            diagnosis_id=response_post.json()["id"],
        ),
        json={"text": "test_text_updated"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == response_post.json()["id"]
    assert response.json()["text"] == "test_text_updated"


@pytest.mark.asyncio()
async def test_delete_diagnosis_node(
    endpoints: conftest.Endpoints,
    client: testclient.TestClient,
) -> None:
    """Tests deleting a diagnosis."""
    diagnosis = {"text": "test_text", "children": []}
    response_parent = client.post(
        endpoints.POST_DIAGNOSIS,
        json={"diagnosis": diagnosis},
    )

    response = client.delete(
        endpoints.DELETE_DIAGNOSIS.format(
            diagnosis_id=response_parent.json()["id"],
        ),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio()
async def test_delete_diagnosis_node_cascade_to_children(
    endpoints: conftest.Endpoints,
    client: testclient.TestClient,
    session: orm.Session,
) -> None:
    """Tests deleting a diagnosis node cascades to children."""
    diagnosis = {
        "text": "test_text",
        "children": [
            {
                "text": "test_child_1",
                "children": [],
            },
        ],
    }
    response_post = client.post(
        endpoints.POST_DIAGNOSIS,
        json={"diagnosis": diagnosis},
    )
    child_id = response_post.json()["children"][0]["id"]
    client.delete(
        endpoints.DELETE_DIAGNOSIS.format(
            diagnosis_id=response_post.json()["id"],
        ),
    )

    child = session.get(models.DiagnosisNode, child_id)

    assert child is None


@pytest.mark.asyncio()
async def test_delete_diagnosis_node_child_no_parent_cascade(
    endpoints: conftest.Endpoints,
    client: testclient.TestClient,
    session: orm.Session,
) -> None:
    """Tests deleting a diagnosis node child does not delete the parent."""
    diagnosis = {
        "text": "test_text",
        "children": [
            {
                "text": "test_child_1",
                "children": [],
            },
        ],
    }
    response_post = client.post(
        endpoints.POST_DIAGNOSIS,
        json={"diagnosis": diagnosis},
    )
    parent_id = response_post.json()["id"]
    child_id = response_post.json()["children"][0]["id"]
    client.delete(
        endpoints.DELETE_DIAGNOSIS.format(
            diagnosis_id=child_id,
        ),
    )

    parent = session.get(models.DiagnosisNode, parent_id)

    assert isinstance(parent, models.DiagnosisNode)
