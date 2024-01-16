"""View definitions for the diagnoses router."""
import logging

import fastapi
from fastapi import status
from sqlalchemy import orm

from ctk_api.core import config
from ctk_api.microservices import sql
from ctk_api.routers.diagnoses import controller, models, schemas

settings = config.get_settings()
LOGGER_NAME = settings.LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

router = fastapi.APIRouter(prefix="/diagnoses", tags=["diagnoses"])


@router.get(
    "",
    description="Gets the dictionary of diagnoses.",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.DiagnosisNodeOutput],
)
async def get_diagnoses(
    session: orm.Session = fastapi.Depends(sql.get_session),
) -> list[models.DiagnosisNode]:
    """Gets the dictionary of diagnoses.

    Returns:
        The dictionary of diagnoses.
    """
    logger.debug("Getting diagnoses.")
    diagnoses = controller.get_diagnoses(session)
    logger.debug("Got diagnoses.")
    return diagnoses


@router.post(
    "",
    summary="Creates a new node in the diagnosis tree.",
    description="""Creates a new diagnosis node. Provide the identifier of the parent
    diagnosis node to create a child node, or no identifier for a root node.""",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The parent diagnosis node was not found.",
        },
    },
)
async def create_diagnosis_node(
    diagnosis: schemas.DiagnosisNodeCreate,
    parent_id: int | None = fastapi.Body(
        None,
        description="""The identifier of the parent diagnosis node.
            Leave blank to create a root node.""",
    ),
    session: orm.Session = fastapi.Depends(sql.get_session),
) -> schemas.DiagnosisNodeOutput:
    """Creates a new diagnosis.

    Args:
        diagnosis: The diagnosis to create.
        parent_id: The identifier of the parent diagnosis node. If
            None, the diagnosis is created as a root node.
        session: The database session.

    Returns:
        The created diagnosis.
    """
    logger.debug("Creating diagnosis.")
    response = controller.create_diagnosis_node(
        diagnosis,
        parent_id,
        session,
    )
    logger.debug("Created diagnosis.")
    return response


@router.patch(
    "/{diagnosis_id}",
    summary="Updates the text of a diagnosis.",
    description="Updates the text of a diagnosis selected by its identifier.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The diagnosis was not found.",
        },
    },
)
async def patch_diagnosis_node(
    patch: schemas.DiagnosisNodePatch = fastapi.Body(
        ...,
        description="The new data to add to the node.",
    ),
    diagnosis_id: int = fastapi.Path(
        description="The identifier of the diagnosis to update.",
    ),
    session: orm.Session = fastapi.Depends(sql.get_session),
) -> schemas.DiagnosisNodeOutput:
    """Updates a diagnosis.

    Args:
        patch: The patch for the diagnosis.
        diagnosis_id: The ID of the diagnosis to update.
        session: The database session.

    Returns:
        The updated diagnosis.
    """
    logger.debug("Updating diagnosis %s.", diagnosis_id)
    response = controller.patch_diagnosis_node(
        diagnosis_id,
        patch,
        session,
    )
    logger.debug("Updated diagnosis %s.", diagnosis_id)
    return response


@router.delete(
    "/{diagnosis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes a diagnosis.",
    description="Deletes a diagnosis selected by its identifier.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The diagnosis was not found.",
        },
    },
)
async def delete_diagnosis_node(
    diagnosis_id: int,
    session: orm.Session = fastapi.Depends(sql.get_session),
) -> None:
    """Deletes a diagnosis.

    Args:
        diagnosis_id: The ID of the diagnosis to delete.
        session: The database session.
    """
    logger.debug("Deleting diagnosis.")
    controller.delete_diagnosis_node(diagnosis_id, session)
    logger.debug("Deleted diagnosis.")
