output "region" {
  value = var.region
}

output "raw_bucket" {
  value = aws_s3_bucket.raw.bucket
}

output "model_bucket" {
  value = aws_s3_bucket.models.bucket
}

output "train_repo_url" {
  value = aws_ecr_repository.train.repository_url
}

output "training_subnets" {
  value = aws_subnet.private[*].id
}

output "training_security_groups" {
  value = [aws_security_group.sagemaker.id]
}


