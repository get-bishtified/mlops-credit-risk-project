import boto3
import time
import os

REGION = os.getenv("AWS_REGION", "ap-south-1")
PROJECT = os.getenv("PROJECT", "credit-mlops")

ROLE_ARN = os.getenv("SAGEMAKER_ROLE_ARN")
TRAIN_IMAGE = os.getenv("TRAIN_IMAGE")
RAW_BUCKET = os.getenv("RAW_BUCKET")
MODEL_BUCKET = os.getenv("MODEL_BUCKET")

missing = []
for k, v in {
    "SAGEMAKER_ROLE_ARN": ROLE_ARN,
    "TRAIN_IMAGE": TRAIN_IMAGE,
    "RAW_BUCKET": RAW_BUCKET,
    "MODEL_BUCKET": MODEL_BUCKET,
}.items():
    if not v:
        missing.append(k)

if missing:
    raise RuntimeError(
        f"Missing required environment variables for training job: {', '.join(missing)}"
    )

sm = boto3.client("sagemaker", region_name=REGION)

job_name = f"{PROJECT}-train-{int(time.time())}"
print(f"Starting training job: {job_name}")

sm.create_training_job(
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
                    "S3Uri": f"s3://{RAW_BUCKET}/train/data.csv",
                    "S3DataDistributionType": "FullyReplicated",
                }
            },
            "ContentType": "text/csv",
        }
    ],
    OutputDataConfig={"S3OutputPath": f"s3://{MODEL_BUCKET}/artifacts"},
    ResourceConfig={
        "InstanceType": "ml.m5.large",
        "InstanceCount": 1,
        "VolumeSizeInGB": 20,
    },
    StoppingCondition={"MaxRuntimeInSeconds": 3600},
)

while True:
    d = sm.describe_training_job(TrainingJobName=job_name)
    status = d["TrainingJobStatus"]
    print("Training status:", status)

    if status == "Completed":
        break
    if status in ("Failed", "Stopped"):
        raise RuntimeError(f"Training job ended with status: {status}")

    time.sleep(60)

artifact = d["ModelArtifacts"]["S3ModelArtifacts"]
print("Model artifact:", artifact)

with open(".env_artifacts", "w") as f:
    f.write(f"MODEL_ARTIFACTS={artifact}\n")
