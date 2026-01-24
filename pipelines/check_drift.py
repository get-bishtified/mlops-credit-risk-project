import boto3, os, datetime

REGION = os.getenv("AWS_REGION", "ap-south-1")
ENDPOINT = os.getenv("ENDPOINT_NAME")

cw = boto3.client("cloudwatch", region_name=REGION)

resp = cw.get_metric_statistics(
    Namespace="AWS/SageMaker",
    MetricName="Invocation4XXErrors",
    Dimensions=[{"Name": "EndpointName", "Value": ENDPOINT}],
    StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
    EndTime=datetime.datetime.utcnow(),
    Period=300,
    Statistics=["Sum"],
)

errors = sum(p["Sum"] for p in resp.get("Datapoints", []))

if errors > 5:
    raise RuntimeError(f"Endpoint unhealthy: {errors} errors")

print("Endpoint healthy")
