# Registry only – models & endpoints are created by the pipeline (boto3)

resource "aws_sagemaker_model_package_group" "this" {
  model_package_group_name        = "${var.project}-credit-risk"
  model_package_group_description = "Credit Risk MLOps Model Group"
}

output "sagemaker_role_arn" {
  value = aws_iam_role.sagemaker_role.arn
}

output "model_package_group_name" {
  value = aws_sagemaker_model_package_group.this.model_package_group_name
}

# Logical name – actual endpoint is created by deploy.py
output "endpoint_name" {
  value = "${var.project}-endpoint"
}
