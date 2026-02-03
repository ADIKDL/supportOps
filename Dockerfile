FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ruff.toml ./
RUN pip install --no-cache-dir --upgrade pip &&     pip install --no-cache-dir -e .

COPY app app
COPY migrations migrations
COPY alembic.ini ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
