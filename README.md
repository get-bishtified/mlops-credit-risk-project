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
- IAM role attached to Jenkins EC2 with:
  - `AdministratorAccess` (lab/demo) **or**
  - Fine-grained permissions for:
    - SageMaker
    - ECR
    - S3
    - IAM:PassRole

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
├── data/                 # Sample CSV
├── tests/                # Pytest checks
├── Jenkinsfile
└── README.md
```

---

## Deployment Flow (APPLY)

1. Jenkins checkout & tests
2. Terraform provisions infra
3. S3 training data ensured
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
0.0   # (example prediction)
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

Running **DESTROY** will permanently delete:

- SageMaker endpoints
- Training jobs
- Model package groups
- S3 buckets (emptied first)
- ECR repositories (images deleted first)
- IAM roles created by Terraform

❗ **This action is irreversible**

A manual Jenkins confirmation is required before destroy executes.

---

## Enterprise Notes

- No credentials hardcoded
- Image versioning supported
- Safe cleanup before destroy
- Ready for GitOps extension
- Can be extended with:
  - Model monitoring
  - Drift detection
  - CI policy enforcement


