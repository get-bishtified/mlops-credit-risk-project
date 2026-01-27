FROM python:3.9-slim

RUN pip install --no-cache-dir \
    sagemaker-inference \
    numpy \
    pandas \
    scikit-learn