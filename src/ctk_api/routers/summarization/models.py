"""Models for the diagnoses router."""
import sqlalchemy
from sqlalchemy import orm

from ctk_api.core import models as base_models


class Summary(base_models.BaseTable):
    """Represents a node in the diagnoses tree.

    Attributes:
        id: The ID of the diagnosis.
        anonymous_text: The text sent to GPT.
        summary_text: The text returned from GPT.

    """

    __tablename__ = "summaries"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)  # noqa: A003
    anonymous_text: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(65536))
    summary_text: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String(65536))
