import os
import time
import boto3

REQUIRED = [
    "SAGEMAKER_ROLE_ARN",
    "TRAIN_IMAGE",
    "RAW_BUCKET",
    "MODEL_BUCKET",
    "TRAINING_SUBNETS",
    "TRAINING_SG",
]

missing = [k for k in REQUIRED if not os.getenv(k)]
if missing:
    raise RuntimeError(
        f"Missing required environment variables for training job: {', '.join(missing)}"
    )

ROLE_ARN      = os.getenv("SAGEMAKER_ROLE_ARN")
TRAIN_IMAGE   = os.getenv("TRAIN_IMAGE")
RAW_BUCKET    = os.getenv("RAW_BUCKET")
MODEL_BUCKET  = os.getenv("MODEL_BUCKET")
SUBNETS_RAW   = os.getenv("TRAINING_SUBNETS")
SG            = os.getenv("TRAINING_SG")

subnet_ids = [s for s in SUBNETS_RAW.split(",") if s]

region = os.getenv("AWS_REGION", "ap-south-1")
sm = boto3.client("sagemaker", region_name=region)

job_name = f"credit-mlops-train-{int(time.time())}"

print(f"Starting training job: {job_name}")
print("ROLE_ARN:", ROLE_ARN)
print("TRAIN_IMAGE:", TRAIN_IMAGE)
print("RAW_BUCKET:", RAW_BUCKET)
print("MODEL_BUCKET:", MODEL_BUCKET)
print("SUBNETS:", subnet_ids)
print("SECURITY_GROUP:", SG)

sm.create_training_job(
    TrainingJobName=job_name,
    RoleArn=ROLE_ARN,
    AlgorithmSpecification={
        "TrainingImage": TRAIN_IMAGE,
        "TrainingInputMode": "File",
        "TrainingImageConfig": {
            "TrainingRepositoryAccessMode": "Vpc"
        }
    },
    VpcConfig={
        "Subnets": subnet_ids,
        "SecurityGroupIds": [SG]
    },
    InputDataConfig=[
        {
            "ChannelName": "train",
            "DataSource": {
                "S3DataSource": {
                    "S3DataType": "S3Prefix",
                    "S3Uri": f"s3://{RAW_BUCKET}/train/",
                    "S3DataDistributionType": "FullyReplicated"
                }
            },
            "ContentType": "text/csv"
        }
    ],
    OutputDataConfig={
        "S3OutputPath": f"s3://{MODEL_BUCKET}/artifacts/"
    },
    ResourceConfig={
        "InstanceType": "ml.m5.large",
        "InstanceCount": 1,
        "VolumeSizeInGB": 30
    },
    StoppingCondition={
        "MaxRuntimeInSeconds": 3600
    }
)

with open(".env_artifacts", "w") as f:
    f.write(f"TRAINING_JOB_NAME={job_name}\n")
    f.write(f"MODEL_ARTIFACTS=s3://{MODEL_BUCKET}/artifacts/\n")

print("Training job submitted successfully.")
