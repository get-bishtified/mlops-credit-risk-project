FROM python:3.8

RUN yum update && yum install -y \
    libgomp1 \
    libglib2.0-0 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    sagemaker-inference \
    numpy \
    pandas \
    scikit-learn

# Verify sagemaker-inference is installed
RUN python -c "import sagemaker_inference.server; print('sagemaker_inference installed')"