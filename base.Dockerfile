FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    git+https://github.com/aws/sagemaker-inference-toolkit.git \
    numpy \
    pandas \
    scikit-learn

# Verify sagemaker-inference is installed
RUN python3 -c "import sagemaker_inference.server; print('sagemaker_inference installed')"