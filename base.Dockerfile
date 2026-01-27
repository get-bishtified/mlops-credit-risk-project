FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    sagemaker-inference \
    numpy \
    pandas \
    scikit-learn

# Verify sagemaker-inference is installed
RUN python3 -c "import sagemaker_inference.server; print('sagemaker_inference installed')"