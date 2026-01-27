FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt/ml/code

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Bind pip to python3 explicitly
RUN python3 -m pip install --upgrade pip

# Core ML + SageMaker runtime
RUN python3 -m pip install --no-cache-dir \
    numpy \
    pandas \
    scikit-learn \
    git+https://github.com/aws/sagemaker-inference-toolkit.git
