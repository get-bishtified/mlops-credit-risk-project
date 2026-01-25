import os
import boto3

required = ["MODEL_ARTIFACTS", "MODEL_GROUP", "INFERENCE_IMAGE"]
missing = [k for k in required if not os.getenv(k)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

MODEL_ARTIFACTS = os.getenv("MODEL_ARTIFACTS")
MODEL_GROUP = os.getenv("MODEL_GROUP")
INFERENCE_IMAGE = os.getenv("INFERENCE_IMAGE")

region = os.getenv("AWS_REGION", "ap-south-1")
sm = boto3.client("sagemaker", region_name=region)

print("Registering model:")
print("  Artifacts:", MODEL_ARTIFACTS)
print("  Group:", MODEL_GROUP)
print("  Inference Image:", INFERENCE_IMAGE)

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
