#!/bin/bash
export SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/312850677728/x-inc-ai-parser-queue-dev"
export S3_BUCKET_NAME="x-inc-ai-parser-idp-data-dev"
export DYNAMODB_TABLE_NAME="x-inc-ai-parser-idempotency-dev"

echo "Variables set. Starting worker..."
python3 services/extraction-worker/src/main.py
