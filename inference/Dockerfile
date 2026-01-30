FROM python:3.9

WORKDIR /opt/ml/code

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir \
    flask \
    gunicorn \
    joblib \
    numpy \
    pandas \
    scikit-learn

COPY app.py .

EXPOSE 8080
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
