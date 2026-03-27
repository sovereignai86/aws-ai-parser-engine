# ------------------------------------------------------------------------------
# 1. Core Modules
# ------------------------------------------------------------------------------
module "network" {
  source       = "./modules/network"
  environment  = var.environment
  project_name = var.project_name
}

module "storage" {
  source       = "./modules/storage"
  environment  = var.environment
  project_name = var.project_name
}

module "messaging" {
  source       = "./modules/messaging"
  environment  = var.environment
  project_name = var.project_name
}

# ------------------------------------------------------------------------------
# 2. Automation: S3 Event Notifications to SQS
# ------------------------------------------------------------------------------

# Allow S3 to send messages to your specific SQS queue
resource "aws_sqs_queue_policy" "s3_to_sqs_policy" {
  queue_url = module.messaging.sqs_queue_url

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "s3.amazonaws.com" }
        Action    = "sqs:SendMessage"
        Resource  = "arn:aws:sqs:us-east-1:312850677728:x-inc-ai-parser-queue-dev"
        Condition = {
          ArnLike = { "aws:SourceArn": "arn:aws:s3:::x-inc-ai-parser-idp-data-dev" }
        }
      }
    ]
  })
}

# Link the Bucket to the Queue
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = "x-inc-ai-parser-idp-data-dev"

  queue {
    queue_arn     = "arn:aws:sqs:us-east-1:312850677728:x-inc-ai-parser-queue-dev"
    events        = ["s3:ObjectCreated:*"]
  }
  
  depends_on = [aws_sqs_queue_policy.s3_to_sqs_policy]
}

# ------------------------------------------------------------------------------
# 3. Global Outputs
# ------------------------------------------------------------------------------
output "ingest_bucket_name" {
  value = module.storage.ingest_bucket_name
}

output "sqs_queue_url" {
  value = module.messaging.sqs_queue_url
}
