FROM python:3.11-slim

WORKDIR /app

COPY poetry.lock pyproject.toml README.md /app
COPY results_dashboard /app/results_dashboard

RUN pip install poetry

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

EXPOSE 8050

CMD ["poetry", "run", "results-dashboard-container"]

