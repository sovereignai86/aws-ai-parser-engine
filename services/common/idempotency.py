import boto3
import hashlib
import time
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class IdempotencyEngine:
    def __init__(self, table_name: str, region_name: str = "us-east-1"):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        
    def generate_hash(self, file_bytes: bytes) -> str:
        """Generate a SHA-256 hash of the file content."""
        return hashlib.sha256(file_bytes).hexdigest()

    def lock_file(self, content_hash: str, s3_key: str, ttl_days: int = 30) -> bool:
        """
        Attempts to write the hash to DynamoDB. 
        Returns True if successful (new file), False if it already exists (duplicate).
        """
        expires_at = int(time.time()) + (ttl_days * 86400)
        
        try:
            self.table.put_item(
                Item={
                    'content_hash': content_hash,
                    's3_key': s3_key,
                    'processed_at': int(time.time()),
                    'expires_at': expires_at
                },
                ConditionExpression='attribute_not_exists(content_hash)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"Idempotency blocked duplicate file hash: {content_hash}")
                return False
            raise e
