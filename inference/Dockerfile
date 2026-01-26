FROM public.ecr.aws/sagemaker/scikit-learn:1.2-1-cpu-py3

RUN pip install --no-cache-dir joblib numpy

COPY serve.py /opt/ml/code/serve.py
ENV SAGEMAKER_PROGRAM serve.py
