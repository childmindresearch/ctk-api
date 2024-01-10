"""Schemas for the diagnoses endpoints."""

import pydantic


class DiagnosisNodeCreate(pydantic.BaseModel):
    """Schema for creating a new node.

    Attributes:
        text: The text of the diagnosis node.
        children: The children of the diagnosis node.
    """

    text: str = pydantic.Field(
        ...,
        json_schema_extra={
            "example": "Autism Spectrum Disorder",
            "description": "The text of the diagnosis node.",
        },
    )
    children: list["DiagnosisNodeCreate"] = pydantic.Field(
        [],
        json_schema_extra={
            "description": "The children of the diagnosis node.",
        },
    )


class DiagnosisNodePatch(pydantic.BaseModel):
    """Schema for patching an existing node.

    Attributes:
        text: The new text of the diagnosis node.
    """

    text: str = pydantic.Field(
        ...,
        json_schema_extra={
            "example": "Autism Spectrum Disorder",
            "description": "The new text of the diagnosis node.",
        },
    )


class DiagnosisNodeOutput(pydantic.BaseModel):
    """Represents the return schema for a diagnosis node.

    Attributes:
        text: The text of the diagnosis node.
        children: The children of the diagnosis node.
    """

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int = pydantic.Field(  # noqa: A003
        ...,
        json_schema_extra={
            "example": 1,
            "description": "The identifier of the diagnosis.",
        },
    )
    text: str = pydantic.Field(
        ...,
        json_schema_extra={
            "example": "Autism Spectrum Disorder",
            "description": "The text of the diagnosis.",
        },
    )
    parent_id: int | None = pydantic.Field(
        None,
        json_schema_extra={
            "example": 1,
            "description": "The identifier of the parent diagnosis node.",
        },
    )
    children: list["DiagnosisNodeOutput"] = pydantic.Field(
        [],
        json_schema_extra={
            "description": "The subclasses of the diagnosis.",
        },
    )
