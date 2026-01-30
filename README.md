# Credit Risk MLOps Pipeline (AWS SageMaker + Jenkins + Terraform)

This repository implements a **production-grade end-to-end MLOps pipeline** for a **Credit Risk prediction system**, reflecting how real enterprises build, deploy, operate, and safely destroy machine learning systems.

---

## 🧠 What This Project Does

The system predicts the **probability of loan default** using features such as:
- Age
- Income
- Loan amount
- Repayment behavior

This helps organizations decide whether a loan should be approved, priced higher, or flagged as high risk.

---

## 🏗️ Why This Is a Real MLOps Project

This project demonstrates:
- Infrastructure provisioning with Terraform
- CI/CD for ML using Jenkins
- Automated training, evaluation, and registration
- SageMaker endpoint deployment
- Secure data handling with S3 & Secrets Manager
- Containerized training and inference
- Safe destroy workflows with cleanup

---

## 🧰 Tech Stack
AWS SageMaker, Jenkins, Terraform, Docker, ECR, S3, IAM, CloudWatch, Python (scikit-learn)

---

## 🔧 Prerequisites

### AWS & Jenkins
- AWS account with SageMaker, S3, ECR, IAM, CloudWatch access
- Jenkins running on EC2 with:
  - Docker
  - Terraform
  - Python 3.8+
  - IAM instance role (no hardcoded credentials)

---

### S3 Training Data (MANDATORY)

Training data must exist in S3.

Expected location:
```
s3://credit-mlops-raw-data/train/data.csv
```

Data can be:
- Copied from a secure source bucket, or
- Taken from `data/sample.csv` as fallback

Optional:
- Store secure S3 URI in Secrets Manager under `data-s3-uri`

⚠️ Training will fail if data is missing.

---

## 🚀 Deployment Steps

1. Upload or configure training data
2. Run Jenkins with ACTION=APPLY
3. Approve deployment when prompted
4. Test endpoint `/ping` and `/invocations`
5. Monitor CloudWatch logs

---

## 🧪 Testing

Health check:
```
curl http://<endpoint-url>/ping
```

Prediction:
```
curl -X POST http://<endpoint-url>/invocations -d "25,30000,10000"
```

---

## 🧹 Destroy Requirements

### Model Package Cleanup

Before destroy:
```
aws sagemaker list-model-packages --model-package-group-name credit-mlops-credit-risk
```

Delete any remaining packages manually.

---

### Destroy Warning ⚠️

DESTROY removes all infrastructure, data, images, and models.
Use only in non-production environments.

---

## 🎓 Learning Outcomes
- End-to-end ML system lifecycle
- Production MLOps workflows
- SageMaker operational constraints
- Safe infrastructure teardown

---

Happy building 🚀
