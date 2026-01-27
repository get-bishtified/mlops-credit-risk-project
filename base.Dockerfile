FROM python:3.8-slim

RUN pip install --no-cache-dir \
    sagemaker-inference \
    numpy \
    pandas \
    scikit-learn

# Verify sagemaker-inference is installed
RUN python -c "import sagemaker_inference.server; print('sagemaker_inference installed')"