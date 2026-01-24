# ==============================
# SageMaker – Training, Registry, Endpoint + Monitoring
# ==============================

locals {
  model_group = "${var.project}-credit-risk"
}

resource "aws_sagemaker_model_package_group" "this" {
  model_package_group_name = local.model_group
}

# Endpoint data capture for monitoring
resource "aws_sagemaker_endpoint_configuration" "prod" {
  name = "${var.project}-endpoint-config"

  production_variants {
    variant_name           = "AllTraffic"
    model_name             = aws_sagemaker_model.prod.name
    initial_instance_count = 1
    instance_type          = "ml.m5.large"
  }

  data_capture_config {
    enable_capture = true

    destination_s3_uri = "s3://${aws_s3_bucket.models.bucket}/monitoring"

    capture_options {
      capture_mode = "Input"
    }

    capture_options {
      capture_mode = "Output"
    }

    initial_sampling_percentage = 100
  }
}

# CloudWatch alarms for endpoint health
resource "aws_cloudwatch_metric_alarm" "endpoint_4xx" {
  alarm_name          = "${var.project}-endpoint-4xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Invocation4XXErrors"
  namespace           = "AWS/SageMaker"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
}

resource "aws_cloudwatch_metric_alarm" "endpoint_5xx" {
  alarm_name          = "${var.project}-endpoint-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Invocation5XXErrors"
  namespace           = "AWS/SageMaker"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
}

output "endpoint_name" {
  value = aws_sagemaker_endpoint.prod.name
}