FROM python:3.9
WORKDIR /app
RUN pip install joblib numpy
COPY predict.py .
CMD ["python", "predict.py"]
