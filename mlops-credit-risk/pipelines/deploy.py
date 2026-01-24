import boto3
import os
import time

REGION = os.getenv("AWS_REGION", "ap-south-1")
ENDPOINT = os.getenv("ENDPOINT_NAME")
MODEL_PACKAGE_ARN = os.getenv("MODEL_PACKAGE_ARN")
ROLE_ARN = os.getenv("SAGEMAKER_ROLE_ARN")

sm = boto3.client("sagemaker", region_name=REGION)

model_name = f"prod-model-{int(time.time())}"
config_name = f"prod-config-{int(time.time())}"

sm.create_model(
    ModelName=model_name,
    ExecutionRoleArn=ROLE_ARN,
    Containers=[{
        "ModelPackageName": MODEL_PACKAGE_ARN
    }]
)

sm.create_endpoint_config(
    EndpointConfigName=config_name,
    ProductionVariants=[{
        "VariantName": "AllTraffic",
        "ModelName": model_name,
        "InitialInstanceCount": 1,
        "InstanceType": "ml.m5.large",
    }],
    DataCaptureConfig={
        "EnableCapture": True,
        "DestinationS3Uri": "s3://" + os.getenv("MODEL_BUCKET") + "/monitoring",
        "InitialSamplingPercentage": 100,
        "CaptureOptions": [{"CaptureMode": "Input"}, {"CaptureMode": "Output"}],
    },
)

sm.update_endpoint(
    EndpointName=ENDPOINT,
    EndpointConfigName=config_name
)

print("Deployment with monitoring enabled:", ENDPOINT)
```python
import boto3
import os
import time

REGION = os.getenv("AWS_REGION", "ap-south-1")
ENDPOINT = os.getenv("ENDPOINT_NAME")
MODEL_PACKAGE_ARN = os.getenv("MODEL_PACKAGE_ARN")
ROLE_ARN = os.getenv("SAGEMAKER_ROLE_ARN")

sm = boto3.client("sagemaker", region_name=REGION)

model_name = f"prod-model-{int(time.time())}"
config_name = f"prod-config-{int(time.time())}"

sm.create_model(
    ModelName=model_name,
    ExecutionRoleArn=ROLE_ARN,
    Containers=[{
        "ModelPackageName": MODEL_PACKAGE_ARN
    }]
)

sm.create_endpoint_config(
    EndpointConfigName=config_name,
    ProductionVariants=[{
        "VariantName": "AllTraffic",
        "ModelName": model_name,
        "InitialInstanceCount": 1,
        "InstanceType": "ml.m5.large",
    }]
)

sm.update_endpoint(
    EndpointName=ENDPOINT,
    EndpointConfigName=config_name
)

print("Deployment triggered for endpoint:", ENDPOINT)
```python
print("Deploy model to SageMaker Endpoint (placeholder)")