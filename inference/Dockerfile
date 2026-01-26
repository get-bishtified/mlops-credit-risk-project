FROM public.ecr.aws/sagemaker/sagemaker-inference:latest

# Install your ML dependencies
RUN pip install --no-cache-dir joblib numpy

# Copy your hook script
COPY serve.py /opt/ml/code/serve.py

# Tell SageMaker which program to load
ENV SAGEMAKER_PROGRAM serve.py
