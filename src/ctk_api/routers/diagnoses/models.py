"""Models for the diagnoses router."""
import sqlalchemy
from sqlalchemy import orm

from ctk_api.core import models as base_models


class DiagnosisNode(base_models.BaseTable):
    """Represents a node in the diagnoses tree.

    Attributes:
        id: The ID of the diagnosis.
        text: The text associated with the diagnosis.
        parent_id: The ID of the parent node.
        children: The list of child node IDs.
        parent: The ID of the parent node.
    """

    __tablename__ = "diagnoses"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)  # noqa: A003
    text: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(2048))
    parent_id = orm.mapped_column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("diagnoses.id"),
    )

    children: orm.Mapped[list[int]] = orm.relationship(
        "DiagnosisNode",
        cascade="all, delete-orphan",
    )
    parent = orm.relationship(
        "DiagnosisNode",
        back_populates="children",
        remote_side=[id],
    )
