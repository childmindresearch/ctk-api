"""Schemas for the summarization router."""

import pydantic


class Report(pydantic.BaseModel):
    """A clinical report."""

    text: str = pydantic.Field(..., description="The text of the report to summarize.")
