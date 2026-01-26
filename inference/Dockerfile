ARG SM_BASE_IMAGE
FROM ${SM_BASE_IMAGE}

RUN pip install --no-cache-dir joblib numpy

COPY serve.py /opt/ml/code/serve.py
ENV SAGEMAKER_PROGRAM serve.py
