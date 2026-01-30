# Credit Risk MLOps Pipeline (AWS SageMaker + Jenkins + Terraform)

This repository implements a full end-to-end MLOps pipeline for a Credit Risk prediction use case, designed to reflect real enterprise practices.

---

## Architecture Overview

- **Jenkins (EC2)** – CI/CD orchestrator  
- **Terraform** – Infrastructure provisioning  
- **Amazon S3** – Raw data, model artifacts  
- **Amazon ECR** – Training & inference images  
- **Amazon SageMaker** – Training jobs, model registry, endpoint  
- **CloudWatch** – Logs and metrics  

---

## Prerequisites

### AWS

- AWS account with admin (or equivalent) permissions
- IAM role attached to Jenkins EC2 with fine-grained permissions for:
    - SageMaker
    - ECR
    - S3
    - IAM:PassRole
    - Secrets Manager (read access)

### Secure Training Data Setup (Required)

This project **does not store sample data in the repository**.

Instead, training data must be **manually uploaded** to a **separate, secure S3 bucket** that is **not managed by Terraform**.

This reflects how enterprises handle sensitive or regulated datasets.

#### Steps

1. Create a dedicated S3 bucket (example):
   ```
   bucket-name
   ```

2. Upload the training dataset manually:
   ```
   s3://bucket-name/folder/file.csv
   ```

3. Store the S3 URI in **AWS Secrets Manager**:
   - **Secret name:** `data-s3-uri`
   - **Secret value:**
     ```
      s3://bucket-name/folder/file.csv
     ```

During deployment:
- Jenkins reads this secret
- Copies the dataset into the Terraform-managed **raw training bucket**
- No sensitive paths are hardcoded in code or pipeline

This ensures **secure data handling and auditability**.

---

### Jenkins EC2

- Instance type: **t3.large** (minimum)
- OS: Amazon Linux 2 / Ubuntu 20.04
- Installed:
  - Docker
  - Python 3.8+
  - pip
  - AWS CLI v2
  - Terraform >= 1.4
  - jq

---

### Jenkins Plugins

- Pipeline
- Pipeline: Groovy
- Git
- Credentials Binding

---

## Repository Structure

```
mlops-credit-risk/
├── infra/                # Terraform (S3, ECR, SageMaker, IAM)
├── training/             # Training container
├── inference/            # Inference container (Flask + Gunicorn)
├── pipelines/            # Python orchestration scripts
├── tests/                # Pytest checks
├── Jenkinsfile
└── README.md
```

---

## Deployment Flow (APPLY)

1. Jenkins checkout & tests
2. Terraform provisions infra
3. Secure training data copied from protected S3 bucket
4. Training & inference images built and pushed to ECR
5. SageMaker training job triggered
6. Model evaluated
7. Model registered to Model Package Group
8. Manual approval gate
9. Endpoint deployed
10. Health check executed

---

## Testing the Endpoint

### Get Endpoint Name
```
aws sagemaker list-endpoints
```

### Invoke Endpoint

Create `payload.csv`:
```
35,55000,20000
```

Invoke:
```
aws sagemaker-runtime invoke-endpoint   --endpoint-name credit-mlops-endpoint   --content-type text/csv   --body payload.csv   output.json
```

Expected output:
```
0.0   # example prediction
```

---

## Monitoring

- CloudWatch Logs:
  - `/aws/sagemaker/Endpoints/credit-mlops-endpoint`
- Metrics:
  - Invocations
  - Latency
  - 4XX / 5XX errors

---

## DESTROY – ⚠️ WARNING

Running **DESTROY** will permanently delete all resources created by this project.

Before Terraform destroy executes, the pipeline performs **explicit cleanup**, including:

- Deleting SageMaker endpoints
- Stopping active training jobs
- Deleting model packages from the Model Package Group
- Emptying S3 buckets created by Terraform
- Deleting images from ECR repositories

After cleanup, Terraform removes:
- SageMaker resources
- S3 buckets
- ECR repositories
- IAM roles created by Terraform

❗ **This action is irreversible**  
A manual Jenkins confirmation is required before destroy executes.

---

## Enterprise Notes

- No credentials hardcoded
- Sensitive data isolated from IaC
- Secrets Manager used for secure data references
- Model versions are auditable
- Safe cleanup enforced before destroy
- CI/CD reflects real production MLOps workflows

---
