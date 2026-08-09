FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/

ENV PYTHONUNBUFFERED=1
ENV PORT=7860

CMD ["bash", "-lc", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]