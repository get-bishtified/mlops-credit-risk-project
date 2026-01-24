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

