FROM 683313688378.dkr.ecr.ap-south-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3

RUN pip install --no-cache-dir joblib numpy
COPY serve.py /opt/ml/code/serve.py
ENV SAGEMAKER_PROGRAM serve.py
