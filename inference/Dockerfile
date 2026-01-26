FROM python:3.9-slim

# Install SageMaker inference runtime and deps
RUN pip install --no-cache-dir sagemaker-inference joblib numpy

# Copy your SageMaker hook script
COPY serve.py /opt/ml/code/serve.py

# Tell SageMaker which script to run
ENV SAGEMAKER_PROGRAM serve.py

# Correct entrypoint for SageMaker inference
ENTRYPOINT ["python", "-m", "sagemaker_inference.serve"]
