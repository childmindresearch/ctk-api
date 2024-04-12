Archived as its functionality has been split across https://github.com/childmindresearch/ctk-webapp and https://github.com/childmindresearch/ctk-functions.

# Clinician Toolkit API
[![Build](https://github.com/childmindresearch/ctk-api/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/childmindresearch/ctk-api/actions/workflows/test.yaml?query=branch%3Amain)
![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This repository contains the API code for the clinician toolkit. It is a Python3.11 FastAPI application. It is deployed as a Docker container.

## Getting Started

To get started, clone this repository and run `poetry install` to install the dependencies. Then, run `poetry run uvicorn ctk_api.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src` to start the application. Alternatively, you can run the API with the Docker image by first building the image with `docker build -t ctk-api .` and then running the image with `docker run -p 8000:8000 ctk-api`.

## Deployment

The deployment of this application is handled by the [CTK-Orchestrator repository](https://github.com/childmindresearch/ctk-orchestrator). On each push to main, this repository will be built and deployed to the Github Container Registry.

## Settings

The application is configured using environment variables. The following environment variables are used:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_CHAT_COMPLETION_MODEL`: The name of the OpenAI model to use for chat completion (default: gpt-4).
