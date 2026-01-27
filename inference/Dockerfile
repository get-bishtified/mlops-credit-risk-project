ARG SM_BASE_IMAGE
FROM ${SM_BASE_IMAGE}

RUN pip install --no-cache-dir joblib

COPY serve.py /opt/ml/code/serve.py
ENV SAGEMAKER_PROGRAM serve.py

ENTRYPOINT ["python", "-m", "sagemaker_inference.server"]
