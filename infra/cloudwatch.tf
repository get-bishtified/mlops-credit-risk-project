resource "aws_cloudwatch_metric_alarm" "endpoint_5xx" {
  alarm_name        = "${var.project}-endpoint-5xx-errors"
  alarm_description = "SageMaker endpoint returning 5XX errors"
  namespace         = "AWS/SageMaker"
  metric_name       = "Invocation5XXErrors"

  dimensions = {
    EndpointName = "${var.project}-endpoint"
  }

  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
}
