FROM tensorflow/tensorflow

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY model model

COPY healthy healthy

COPY wc_dataset_processed.csv wc_dataset_processed.csv

COPY predictcontroller.py app.py

EXPOSE 8000

CMD ["python", "app.py"]
