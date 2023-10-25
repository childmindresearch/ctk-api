"""Settings for the API."""
import functools
import logging
import pathlib

import pydantic
import pydantic_settings


class Settings(pydantic_settings.BaseSettings):  # type: ignore[valid-type, misc]
    """Settings for the API."""

    LOGGER_NAME: str = pydantic.Field("Clinician Toolkit API")
    LOGGER_VERBOSITY: int | None = pydantic.Field(
        logging.DEBUG,
        json_schema_extra={"env": "LOGGER_VERBOSITY"},
    )

    ENVIRONMENT: str = pydantic.Field(
        "development",
        json_schema_extra={"env": "CTK_API_ENVIRONMENT"},
    )

    DIAGNOSES_FILE: pathlib.Path = pydantic.Field(
        pathlib.Path(__file__).parent.parent / "data" / "diagnoses.json",
        json_schema_extra={"env": "DIAGNOSES_FILE"},
    )

    OPENAI_API_KEY: pydantic.SecretStr = pydantic.Field(
        ...,
        json_schema_extra={"env": "OPENAI_API_KEY"},
    )
    OPENAI_CHAT_COMPLETION_MODEL: str = pydantic.Field(
        "gpt-4",
        json_schema_extra={"env": "OPENAI_CHAT_COMPLETION_MODEL"},
    )
    OPENAI_CHAT_COMPLETION_SYSTEM_PROMPT_FILE: pathlib.Path = pydantic.Field(
        pathlib.Path(__file__).parent.parent
        / "data"
        / "openai_default_chat_completion_system_prompt.txt",
        json_schema_extra={"env": "OPENAI_CHAT_COMPLETION_SYSTEM_PROMPT_FILE"},
    )

    ELASTIC_URL: pydantic.AnyHttpUrl = pydantic.Field(
        "http://localhost:9200",
        json_schema_extra={"env": "ELASTIC_URL"},
    )
    ELASTIC_USER: str = pydantic.Field(
        "elastic",
        json_schema_extra={"env": "ELASTIC_USER"},
    )
    ELASTIC_PASSWORD: pydantic.SecretStr = pydantic.Field(
        ...,
        json_schema_extra={"env": "ELASTIC_PASSWORD"},
    )

    @pydantic.field_validator("ENVIRONMENT")
    def validate_environment(
        cls,  # noqa: N805
        value: str,
    ) -> str:
        """Validates the environment.

        Args:
            value: The environment to validate.

        Returns:
            The validated environment.

        Raises:
            ValueError: If the environment is not valid.
        """
        if value in {"development", "staging", "production"}:
            return value
        msg = "Environment must be either 'development', 'staging', or 'production'."
        raise ValueError(msg)


@functools.lru_cache
def get_settings() -> Settings:
    """Cached fetcher for the API settings.

    Returns:
        The settings for the API.
    """
    return Settings()  # type: ignore[call-arg]


def initialize_logger() -> None:
    """Initializes the logger for the API."""
    settings = get_settings()
    logger = logging.getLogger(settings.LOGGER_NAME)
    if settings.LOGGER_VERBOSITY is not None:
        logger.setLevel(settings.LOGGER_VERBOSITY)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)s - %(funcName)s - %(message)s",  # noqa: E501
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
