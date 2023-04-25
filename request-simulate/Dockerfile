FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY healthy healthy

COPY wc_dataset_processed.csv wc_dataset_processed.csv

COPY simulate-request.py app.py

EXPOSE 8000

CMD ["python", "app.py"]