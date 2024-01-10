FROM python:3.11-bullseye

EXPOSE 8000

WORKDIR /app

COPY --from=pandoc/minimal:latest /pandoc /usr/bin/pandoc
COPY pyproject.toml poetry.lock  README.md LICENSE ./
COPY src ./src
COPY tests ./tests

RUN pip install --no-cache-dir .

CMD ["uvicorn", "ctk_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
