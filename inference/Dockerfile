FROM python:3.9-slim

RUN pip install --no-cache-dir \
    sagemaker-inference \
    joblib \
    numpy \
    pandas \
    scikit-learn

COPY serve.py /opt/ml/code/serve.py
ENV SAGEMAKER_PROGRAM serve.py

ENTRYPOINT ["python", "-m", "sagemaker_inference.server"]
