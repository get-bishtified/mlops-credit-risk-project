import boto3
import os
import time

required = [
    "SAGEMAKER_ROLE_ARN",
    "TRAIN_IMAGE",
    "RAW_BUCKET",
    "MODEL_BUCKET",
]

missing = [k for k in required if not os.getenv(k)]
if missing:
    raise RuntimeError(
        f"Missing required environment variables for training job: {', '.join(missing)}"
    )

REGION = os.getenv("AWS_REGION", "ap-south-1")
ROLE_ARN = os.getenv("SAGEMAKER_ROLE_ARN")
TRAIN_IMAGE = os.getenv("TRAIN_IMAGE")
RAW_BUCKET = os.getenv("RAW_BUCKET")
MODEL_BUCKET = os.getenv("MODEL_BUCKET")

sm = boto3.client("sagemaker", region_name=REGION)

job_name = f"credit-mlops-train-{int(time.time())}"
print("Starting training job:", job_name)

response = sm.create_training_job(
    TrainingJobName=job_name,
    RoleArn=ROLE_ARN,
    AlgorithmSpecification={
        "TrainingImage": TRAIN_IMAGE,
        "TrainingInputMode": "File",
    },
    InputDataConfig=[
        {
            "ChannelName": "train",
            "DataSource": {
                "S3DataSource": {
                    "S3DataType": "S3Prefix",
                    "S3Uri": f"s3://{RAW_BUCKET}/train/",
                    "S3DataDistributionType": "FullyReplicated",
                }
            },
            "ContentType": "text/csv",
        }
    ],
    OutputDataConfig={
        "S3OutputPath": f"s3://{MODEL_BUCKET}/artifacts/"
    },
    ResourceConfig={
        "InstanceType": "ml.m5.large",
        "InstanceCount": 1,
        "VolumeSizeInGB": 10,
    },
    StoppingCondition={
        "MaxRuntimeInSeconds": 3600
    },
)

print("Training job submitted successfully:", response["TrainingJobArn"])

model_artifacts = f"s3://{MODEL_BUCKET}/artifacts/{job_name}/output/model.tar.gz"
with open(".env_artifacts", "w") as f:
    f.write(f"MODEL_ARTIFACTS={model_artifacts}\n")
