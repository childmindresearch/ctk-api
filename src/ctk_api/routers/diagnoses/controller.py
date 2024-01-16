"""Controller for the diagnoses endpoint."""
import logging

import fastapi
from fastapi import status
from sqlalchemy import orm

from ctk_api.core import config
from ctk_api.routers.diagnoses import models, schemas

settings = config.get_settings()

LOGGER_NAME = settings.LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME)


def get_diagnoses(
    session: orm.Session,
) -> list[models.DiagnosisNode]:
    """Gets the list of root diagnoses.

    Args:
        session: The SQLAlchemy session.

    Returns:
        The list of root diagnoses.
    """
    logger.debug("Getting diagnoses.")
    return session.query(models.DiagnosisNode).filter_by(parent=None).all()


def create_diagnosis_node(
    diagnosis: schemas.DiagnosisNodeCreate,
    parent_id: int | None,
    session: orm.Session,
    *,
    commit: bool = True,
) -> models.DiagnosisNode:
    """Creates a new diagnosis node.

    Args:
        diagnosis: The diagnosis to create.
        parent_id: The identifier of the parent diagnosis node.
        session: The SQLAlchemy session.
        commit: Whether to commit the session.

    Returns:
        The created diagnosis.

    Raises:
        fastapi.HTTPException: 404 If the parent diagnosis node does not exist.
    """
    logger.debug("Creating diagnosis.")
    children = [
        create_diagnosis_node(child, None, session, commit=False)
        for child in diagnosis.children
    ]
    node = models.DiagnosisNode(
        text=diagnosis.text,
        children=children,
    )

    if parent_id is not None:
        parent = session.get(models.DiagnosisNode, parent_id)
        if parent is None:
            raise fastapi.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified parent diagnosis node does not exist.",
            )
        parent.children.append(node)
    session.add(node)
    if commit:
        session.commit()
    return node


def patch_diagnosis_node(
    identifier: int,
    patch: schemas.DiagnosisNodePatch,
    session: orm.Session,
) -> models.DiagnosisNode:
    """Patches a diagnosis.

    Args:
        identifier: The identifier of the diagnosis node to patch.
        patch: The new schema of the diagnosis node.
        session: The SQLAlchemy session.

    Returns:
        The patched diagnosis.
    """
    logger.debug("Patching diagnosis %s.", identifier)
    diagnosis = session.get(models.DiagnosisNode, identifier)
    if diagnosis is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified diagnosis does not exist.",
        )
    if patch.text is not None:
        diagnosis.text = patch.text

    if patch.parent_id is not None:
        diagnosis.parent = session.get(models.DiagnosisNode, patch.parent_id)
        if diagnosis.parent is None:
            raise fastapi.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified parent diagnosis does not exist.",
            )
        diagnosis.parent_id = diagnosis.parent.id  # type: ignore[assignment]

        traversal = diagnosis.parent
        while traversal is not None:
            if traversal.id == diagnosis.id:  # type: ignore[union-attr]
                raise fastapi.HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot move a diagnosis to a child of itself.",
                )
            traversal = traversal.parent  # type: ignore[union-attr]

    session.commit()
    return diagnosis


def delete_diagnosis_node(identifier: int, session: orm.Session) -> None:
    """Deletes a diagnosis.

    Args:
        identifier: The identifier of the diagnosis to delete.
        session: The SQLAlchemy session.

    Raises:
        fastapi.HTTPException: 404 If the diagnosis does not exist.
    """
    logger.debug("Deleting diagnosis %s.", identifier)

    diagnosis = session.get(models.DiagnosisNode, identifier)
    if diagnosis is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified diagnosis does not exist.",
        )

    session.delete(diagnosis)
    session.commit()
