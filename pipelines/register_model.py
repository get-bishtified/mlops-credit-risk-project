import os
import boto3

# Ensure required environment variables exist
required = ["MODEL_ARTIFACTS", "MODEL_GROUP"]
missing = [k for k in required if not os.getenv(k)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

MODEL_ARTIFACTS = os.getenv("MODEL_ARTIFACTS")
MODEL_GROUP = os.getenv("MODEL_GROUP")

region = os.getenv("AWS_REGION", "ap-south-1")
sm = boto3.client("sagemaker", region_name=region)

print("Registering model from:", MODEL_ARTIFACTS)
print("Model package group:", MODEL_GROUP)

resp = sm.create_model_package(
    ModelPackageGroupName=MODEL_GROUP,
    ModelPackageDescription="Credit risk model",
    InferenceSpecification={
        "Containers": [
            {
                "Image": os.getenv("INFERENCE_IMAGE", os.getenv("TRAIN_IMAGE")),
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
