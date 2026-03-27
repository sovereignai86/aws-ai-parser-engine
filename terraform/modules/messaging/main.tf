# ------------------------------------------------------------------------------
# 1. Dead Letter Queue (Catches Poison Pills)
# ------------------------------------------------------------------------------
resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_name}-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days to review failed docs
}

# ------------------------------------------------------------------------------
# 2. Primary Processing Queue
# ------------------------------------------------------------------------------
resource "aws_sqs_queue" "main" {
  name                       = "${var.project_name}-queue-${var.environment}"
  visibility_timeout_seconds = 300 # 5 minutes for Bedrock/Claude to process

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3 # Move to DLQ after 3 failed attempts
  })
}
