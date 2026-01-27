FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt/ml/code

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

# Bind pip to python3 explicitly
RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --no-cache-dir \
    flask \
    gunicorn \
    gevent \
    numpy \
    pandas \
    scikit-learn

RUN python3 -m pip install --no-cache-dir \
    git+https://github.com/aws/sagemaker-inference-toolkit.git

# Copy your serve script
COPY serve.py /opt/ml/code/serve.py

ENV SAGEMAKER_PROGRAM serve.py

# Always use python3 at runtime
ENTRYPOINT ["python3", "-m", "sagemaker_inference.server"]
