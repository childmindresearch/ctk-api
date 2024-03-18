"""Middleware for the FastAPI application."""

import logging
import uuid

import fastapi
from starlette import types

from ctk_api.core import config

settings = config.get_settings()
logger = logging.getLogger(settings.LOGGER_NAME)


class RequestLoggerMiddleware:  # pylint: disable=too-few-public-methods
    """Middleware that logs incoming requests."""

    def __init__(self, app: fastapi.FastAPI) -> None:
        """Initializes a new instance of the RequestLoggerMiddleware class.

        Args:
            app: The FastAPI instance to apply middleware to.
        """
        self.app = app

    async def __call__(
        self,
        scope: types.Scope,
        receive: types.Receive,
        send: types.Send,
    ) -> None:
        """Middleware method that handles incoming HTTP requests.

        Args:
            scope: The ASGI scope of the incoming request.
            receive: A coroutine that receives incoming messages.
            send: A coroutine that sends outgoing messages.

        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = fastapi.Request(scope, receive=receive)
        request_id = uuid.uuid4()

        logger.info(
            "Starting request: %s - %s - %s",
            request_id,
            request.method,
            request.url.path,
        )

        await self.app(scope, receive, send)

        logger.info("Finished request: %s.", request_id)
