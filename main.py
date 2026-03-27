import sys, os, boto3, json, logging, threading, time, requests, hmac, hashlib
from datetime import datetime

# Path setup for local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from common.pydantic_models import PurchaseOrder
from common.bedrock_client import BedrockExtractor

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

# Enterprise Secrets (Should be in AWS Secrets Manager)
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "xinc-dev-secret-2026")

def send_enterprise_webhook(payload: dict, event_type: str):
    """
    Delivers a signed CloudEvent to the destination.
    This is the Gold Standard for B2B integrations.
    """
    if not WEBHOOK_URL:
        return

    # 1. Wrap in CloudEvents 1.0 Structure
    cloudevent = {
        "specversion": "1.0",
        "type": f"com.x-inc.parser.{event_type}",
        "source": "/extraction/worker/v1",
        "id": payload.get("id", "unknown"),
        "time": datetime.utcnow().isoformat() + "Z",
        "datacontenttype": "application/json",
        "data": payload
    }
    
    body = json.dumps(cloudevent, separators=(',', ':'))
    timestamp = str(int(time.time()))
    
    # 2. Generate HMAC-SHA256 Signature
    # We sign "timestamp.body" to prevent replay attacks
    signature_base = f"{timestamp}.{body}"
    signature = hmac.new(
        WEBHOOK_SECRET.encode(), 
        signature_base.encode(), 
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-XInc-Signature": f"v1={signature}",
        "X-XInc-Timestamp": timestamp,
        "User-Agent": "X-Inc-AI-Parser-Worker/2026.1"
    }

    try:
        resp = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info(f"📡 Webhook Delivered: {resp.status_code}")
    except Exception as e:
        logger.error(f"❌ Webhook Failed: {e}")

class SQSHeartbeat:
    """Maintains message visibility while Claude is thinking."""
    def __init__(self, sqs, url, handle, interval=30, extension=120):
        self.sqs, self.url, self.handle = sqs, url, handle
        self.interval, self.extension = interval, extension
        self.stop_event = threading.Event()

    def __enter__(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop_event.set()
        self.thread.join(timeout=2)

    def _run(self):
        while not self.stop_event.is_set():
            try:
                self.sqs.change_message_visibility(
                    QueueUrl=self.url, ReceiptHandle=self.handle, VisibilityTimeout=self.extension
                )
                logger.debug("❤️ Heartbeat sent.")
            except: break
            self.stop_event.wait(self.interval)

def start_worker():
    sqs = boto3.client('sqs', region_name='us-east-1')
    s3 = boto3.client('s3', region_name='us-east-1')
    db = boto3.resource('dynamodb', region_name='us-east-1')
    extractor = BedrockExtractor()
    
    queue_url = os.environ.get("SQS_QUEUE_URL")
    table = db.Table(os.environ.get("DYNAMODB_TABLE_NAME"))

    logger.info("🚀 Enterprise Worker Online | HITL & Signature Logic Active")

    while True:
        resp = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=20, MaxNumberOfMessages=1)
        for msg in resp.get('Messages', []):
            handle = msg['ReceiptHandle']
            with SQSHeartbeat(sqs, queue_url, handle):
                try:
                    body = json.loads(msg['Body'])
                    for record in body.get('Records', []):
                        bucket = record['s3']['bucket']['name']
                        key = record['s3']['object']['key']
                        
                        logger.info(f"📥 Processing: {key}")
                        file_obj = s3.get_object(Bucket=bucket, Key=key)
                        
                        # AI Extraction via Claude 4.6
                        data = extractor.extract_structured_data(file_obj['Body'].read(), key, PurchaseOrder)
                        
                        # HITL LOGIC: Define status based on AI Confidence
                        status = "PROCESSED" if data.confidence_score >= 0.90 else "PENDING_REVIEW"
                        
                        # DYNAMODB LOGGING
                        item = {
                            'id': key,
                            'status': status,
                            'vendor': data.vendor_name,
                            'total': str(data.grand_total),
                            'confidence': str(data.confidence_score),
                            'extracted_at': datetime.utcnow().isoformat(),
                            'raw_data': data.model_dump()
                        }
                        table.put_item(Item=item)

                        # ENTERPRISE WEBHOOK
                        send_enterprise_webhook(item, event_type="extraction.complete")

                        # S3 ARCHIVE
                        s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=f"processed/{key}")
                        s3.delete_object(Bucket=bucket, Key=key)
                        logger.info(f"✅ Finished {key} as {status}")

                    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=handle)
                except Exception as e:
                    logger.error(f"💥 Critical Error: {e}")
                    send_enterprise_webhook({"error": str(e)}, event_type="extraction.failed")

if __name__ == "__main__":
    start_worker()
