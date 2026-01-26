ARG SM_BASE_IMAGE
FROM ${SM_BASE_IMAGE}

# Install any extra runtime deps
RUN pip install --no-cache-dir joblib numpy pandas scikit-learn

# Copy your serving script
COPY serve.py /opt/ml/code/serve.py

# Tell SageMaker which script to run
ENV SAGEMAKER_PROGRAM serve.py

# Correct SageMaker entrypoint for model serving
ENTRYPOINT ["python", "-m", "sagemaker_inference.server"]
