import hmac
import hashlib
import time
from fastapi import FastAPI, Request, HTTPException, Header
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CLIENT] - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="X-Inc AI Parser - Reference Receiver")

# The Secret Key provided by X-Inc. 
# In a real system, the client would load this from their environment.
SHARED_SECRET = "xinc-dev-secret-2026"
MAX_AGE_SECONDS = 300  # Reject hooks older than 5 minutes

def verify_signature(payload_body: bytes, timestamp: str, signature_header: str) -> bool:
    """Recomputes the HMAC-SHA256 signature and compares it safely."""
    if not signature_header.startswith("v1="):
        return False
        
    extracted_sig = signature_header.split("v1=")[1]
    
    # Rebuild the exact string the sender (X-Inc) signed: "timestamp.body"
    signature_base = f"{timestamp}.".encode('utf-8') + payload_body
    
    # Calculate what the signature *should* be
    expected_sig = hmac.new(
        SHARED_SECRET.encode('utf-8'),
        signature_base,
        hashlib.sha256
    ).hexdigest()
    
    # hmac.compare_digest prevents timing attacks (where hackers guess the key by measuring response times)
    return hmac.compare_digest(expected_sig, extracted_sig)

@app.post("/webhooks/x-inc")
async def receive_invoice_data(
    request: Request,
    x_xinc_signature: str = Header(None),
    x_xinc_timestamp: str = Header(None)
):
    """The endpoint that receives the extracted AI data."""
    if not x_xinc_signature or not x_xinc_timestamp:
        logger.warning("Missing required X-Inc security headers.")
        raise HTTPException(status_code=401, detail="Missing signatures")

    # 1. Prevent Replay Attacks (Check if the timestamp is too old)
    current_time = int(time.time())
    if current_time - int(x_xinc_timestamp) > MAX_AGE_SECONDS:
        logger.warning("Rejected: Webhook timestamp is too old (Possible Replay Attack).")
        raise HTTPException(status_code=400, detail="Timestamp expired")

    # 2. Verify the Cryptographic Signature
    raw_body = await request.body()
    if not verify_signature(raw_body, x_xinc_timestamp, x_xinc_signature):
        logger.error("Rejected: Cryptographic signature mismatch!")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 3. Process the Authentic Data
    payload = await request.json()
    logger.info(f"✅ Verified Payload Received! Event Type: {payload.get('type')}")
    
    # Extract the actual business data
    business_data = payload.get("data", {})
    logger.info(f"💰 Invoice from {business_data.get('vendor')} for ${business_data.get('total')} successfully logged into client system.")

    return {"status": "success", "message": "Webhook verified and processed"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting X-Inc Reference Receiver on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
