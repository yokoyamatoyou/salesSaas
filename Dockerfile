FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# create non-root user
RUN addgroup --system sales \
    && adduser --system --ingroup sales sales

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# adjust permissions and switch to non-root user
RUN chown -R sales:sales /app
USER sales

EXPOSE 8080
HEALTHCHECK CMD curl -fsS http://localhost:8080/_stcore/health || exit 1
ENTRYPOINT ["streamlit", "run", "app/ui.py", "--server.port=8080", "--server.address=0.0.0.0"]

