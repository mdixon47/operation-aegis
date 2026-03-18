FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/app/src

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY app/src/project_velocity ./app/src/project_velocity
COPY README.md ./README.md

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "-m", "project_velocity", "serve", "--host", "0.0.0.0", "--port", "8000"]
