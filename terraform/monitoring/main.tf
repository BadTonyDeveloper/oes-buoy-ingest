terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = "eu-west-3"
}

# SNS Topic for Lambda alarms
resource "aws_sns_topic" "lambda_alarms" {
  name = "oes-lambda-alarms"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.lambda_alarms.arn
  protocol  = "email"
  endpoint  = "ab22crt@bolton.ac.uk"
}

# Lambda Alarm for Ingest Function Errors
resource "aws_cloudwatch_metric_alarm" "ingest_lambda_errors" {
  alarm_name          = "IngestLambdaErrorAlarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Triggers when ingest lambda has one or more errors"
  dimensions = {
    FunctionName = "oes-lambda-ingest-eu-west-3-dev"
  }
  alarm_actions = [aws_sns_topic.lambda_alarms.arn]
}

# Lambda Alarm for Convert Function Duration
resource "aws_cloudwatch_metric_alarm" "convert_lambda_duration" {
  alarm_name          = "ConvertLambdaHighDuration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Average"
  threshold           = 2500
  alarm_description   = "Triggers when convert lambda duration exceeds 2.5s average"
  dimensions = {
    FunctionName = "oes-lambda-convert-container-eu-west-3-dev"
  }
  alarm_actions = [aws_sns_topic.lambda_alarms.arn]
}

# EventBridge Scheduler Failure Alarm
resource "aws_cloudwatch_metric_alarm" "scheduler_invocation_failure" {
  alarm_name          = "SchedulerInvocationFailures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FailedInvocations"
  namespace           = "AWS/Scheduler"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Triggers if EventBridge scheduler fails to invoke a target"
  dimensions = {
    ScheduleGroup = "default"
  }
  alarm_actions = [aws_sns_topic.lambda_alarms.arn]
}