FROM python:3.8

WORKDIR /opt/ml/code

RUN python -m pip install --upgrade pip

# Pin NumPy to a stable wheel and install deps
RUN pip install --no-cache-dir \
    flask \
    gunicorn \
    joblib \
    numpy==1.26.4 \
    pandas \
    scikit-learn

COPY app.py .

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
