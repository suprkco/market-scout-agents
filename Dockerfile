FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY scout scout
COPY data data
RUN mkdir /state && chown appuser /state
USER appuser
CMD ["python", "-m", "scout.cli", "run", "--thread", "demo", "--db", "/state/checkpoints.db"]
