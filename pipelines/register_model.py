import os
import boto3
from botocore.exceptions import ClientError

required = ["MODEL_ARTIFACTS", "MODEL_GROUP", "INFERENCE_IMAGE"]
missing = [k for k in required if not os.getenv(k) or os.getenv(k) in ("", "null", "None")]

if missing:
    raise RuntimeError(
        f"Missing or invalid environment variables: {', '.join(missing)}"
    )

MODEL_ARTIFACTS = os.getenv("MODEL_ARTIFACTS")
MODEL_GROUP = os.getenv("MODEL_GROUP")
INFERENCE_IMAGE = os.getenv("INFERENCE_IMAGE")

region = os.getenv("AWS_REGION", "ap-south-1")
sm = boto3.client("sagemaker", region_name=region)

print("Using model package group:", MODEL_GROUP)

# Ensure group exists
try:
    sm.describe_model_package_group(ModelPackageGroupName=MODEL_GROUP)
    print("Model Package Group already exists.")
except ClientError as e:
    if e.response["Error"]["Code"] == "ValidationException":
        print("Model Package Group not found. Creating...")
        sm.create_model_package_group(
            ModelPackageGroupName=MODEL_GROUP,
            ModelPackageGroupDescription="Credit Risk MLOps Model Group"
        )
    else:
        raise

resp = sm.create_model_package(
    ModelPackageGroupName=MODEL_GROUP,
    ModelPackageDescription="Credit risk model",
    InferenceSpecification={
        "Containers": [
            {
                "Image": INFERENCE_IMAGE,
                "ModelDataUrl": MODEL_ARTIFACTS,
            }
        ],
        "SupportedContentTypes": ["text/csv"],
        "SupportedResponseMIMETypes": ["text/csv"],
    },
    ModelApprovalStatus="PendingManualApproval",
)

model_package_arn = resp["ModelPackageArn"]
print("Created model package:", model_package_arn)

with open(".env_model", "w") as f:
    f.write(f"MODEL_PACKAGE_ARN={model_package_arn}\n")
