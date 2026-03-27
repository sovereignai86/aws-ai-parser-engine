output "ingest_bucket_name" {
  value = aws_s3_bucket.data.bucket
}

output "idempotency_table_name" {
  value = aws_dynamodb_table.idempotency.name
}
