FROM python:3.11-slim

WORKDIR .

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV REPORT_INTERVAL_SECONDS=15

CMD ["python", "app.py"]