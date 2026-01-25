import boto3
import os
import time
from botocore.exceptions import ClientError

required = [
    "AWS_REGION",
    "ENDPOINT_NAME",
    "MODEL_PACKAGE_ARN",
    "SAGEMAKER_ROLE_ARN",
    "MODEL_BUCKET",
]

missing = [k for k in required if not os.getenv(k)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

REGION = os.getenv("AWS_REGION", "ap-south-1")
ENDPOINT = os.getenv("ENDPOINT_NAME")
MODEL_PACKAGE_ARN = os.getenv("MODEL_PACKAGE_ARN")
ROLE_ARN = os.getenv("SAGEMAKER_ROLE_ARN")
MODEL_BUCKET = os.getenv("MODEL_BUCKET")

sm = boto3.client("sagemaker", region_name=REGION)

print("Approving model package:", MODEL_PACKAGE_ARN)
sm.update_model_package(
    ModelPackageArn=MODEL_PACKAGE_ARN,
    ModelApprovalStatus="Approved"
)

model_name = f"prod-model-{int(time.time())}"
config_name = f"prod-config-{int(time.time())}"

print("Creating model:", model_name)
sm.create_model(
    ModelName=model_name,
    ExecutionRoleArn=ROLE_ARN,
    Containers=[{
        "ModelPackageName": MODEL_PACKAGE_ARN
    }]
)

print("Creating endpoint config:", config_name)
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
        "DestinationS3Uri": f"s3://{MODEL_BUCKET}/monitoring",
        "InitialSamplingPercentage": 100,
        "CaptureOptions": [
            {"CaptureMode": "Input"},
            {"CaptureMode": "Output"}
        ],
    },
)

print("Deploying to endpoint:", ENDPOINT)

try:
    sm.update_endpoint(
        EndpointName=ENDPOINT,
        EndpointConfigName=config_name
    )
    print("Endpoint updated.")
except ClientError as e:
    if e.response["Error"]["Code"] == "ValidationException":
        print("Endpoint not found. Creating new endpoint:", ENDPOINT)
        sm.create_endpoint(
            EndpointName=ENDPOINT,
            EndpointConfigName=config_name
        )
        print("Endpoint creation triggered.")
    else:
        raise

print("Deployment flow completed for:", ENDPOINT)
