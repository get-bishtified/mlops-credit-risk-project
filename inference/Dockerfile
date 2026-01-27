FROM python:3.8-slim

RUN pip install --no-cache-dir flask gunicorn joblib numpy pandas scikit-learn

COPY app.py /opt/ml/code/app.py

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
