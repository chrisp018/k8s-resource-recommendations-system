FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY healthy healthy

COPY app-loadtest.py app.py

CMD ["python", "app.py"]
