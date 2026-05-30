FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ ./agents/
COPY docs/fabric_iq_ontology.json ./docs/fabric_iq_ontology.json
COPY synthetic-data/ ./synthetic-data/

CMD ["python", "agents/orchestrator.py"]
