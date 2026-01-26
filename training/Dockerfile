FROM python:3.9-slim

WORKDIR /opt/ml/code

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Training script
COPY train.py .

# SageMaker expects the program name in this env
ENV SAGEMAKER_PROGRAM train.py

# Default command SageMaker uses
ENTRYPOINT ["python", "train.py"]
