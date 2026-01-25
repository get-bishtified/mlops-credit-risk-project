output "region" {
  value = var.region
}

output "raw_bucket" {
  value = aws_s3_bucket.raw.bucket
}

output "model_bucket" {
  value = aws_s3_bucket.models.bucket
}

output "train_image" {
  value = "${aws_ecr_repository.train.repository_url}:latest"
}

output "infer_image" {
  value = "${aws_ecr_repository.infer.repository_url}:latest"
}

output "training_subnets" {
  value = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id
  ]
}

output "training_security_groups" {
  value = [aws_security_group.sagemaker.id]
}



