# Credit Risk MLOps Platform

Enterprise-grade MLOps using:
- Terraform
- AWS SageMaker
- Jenkins
- Docker

Flow:
1. Code pushed to Git
2. Jenkins runs tests
3. Terraform provisions infra
4. SageMaker trains model
5. Model evaluated
6. Manual approval
7. Deployed to production