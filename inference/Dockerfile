ARG BASE_IMAGE
FROM ${BASE_IMAGE}

WORKDIR /opt/ml/code

COPY serve.py /opt/ml/code/serve.py

ENV SAGEMAKER_PROGRAM serve.py

ENTRYPOINT ["python3", "-m", "sagemaker_inference.server"]
