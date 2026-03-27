# ------------------------------------------------------------------------------
# 1. S3 Bucket for Document Pipeline
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "data" {
  bucket = "${var.project_name}-idp-data-${var.environment}"
  force_destroy = true 
}

resource "aws_s3_bucket_lifecycle_configuration" "data_lifecycle" {
  bucket = aws_s3_bucket.data.id

  rule {
    id     = "archive-to-glacier"
    status = "Enabled"

    filter {
      prefix = "archive/"
    }

    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }

  rule {
    id     = "delete-poison-pills"
    status = "Enabled"

    filter {
      prefix = "failed/"
    }

    expiration {
      days = 14
    }
  }
}

# ------------------------------------------------------------------------------
# 2. DynamoDB Table for Idempotency (Exactly-Once Processing)
# ------------------------------------------------------------------------------
resource "aws_dynamodb_table" "idempotency" {
  name         = "${var.project_name}-idempotency-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "content_hash"

  attribute {
    name = "content_hash"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
}
