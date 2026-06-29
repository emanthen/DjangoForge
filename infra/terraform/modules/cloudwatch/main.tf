resource "aws_cloudwatch_log_group" "web" {
  name              = "/${var.app_name}/web"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/${var.app_name}/worker"
  retention_in_days = 30
}

resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.app_name}-ecs-cpu-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 120
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization > 80%"
  dimensions = {
    ClusterName = var.ecs_cluster
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.app_name}-alb-5xx-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "ALB 5xx errors > 10 per minute"
  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }
}
