
2. Configure Your Secret

In a production environment, you must securely store the shared secret provided by your X-Inc account manager. For this local test, it defaults to xinc-dev-secret-2026.

3. Run the Server

Start the local FastAPI server:

Bash

python3 app.py 

The server will start listening on http://0.0.0.0:8000/webhooks/x-inc.

🛡️ Security Architecture: How It Works

When the X-Inc AI Parser finishes extracting a document, it sends an HTTP POST request to your endpoint. We utilize the CloudEvents 1.0 specification.

Every request includes two critical security headers:

X-XInc-Timestamp: The exact Unix timestamp when the event was fired.

X-XInc-Signature: The cryptographic hash proving authenticity.

The Verification Process

Your receiver must perform three checks before accepting the data (all demonstrated in app.py):

Timestamp Validation: The receiver checks if Current_Time - X-XInc-Timestamp > 300 seconds. If the payload is older than 5 minutes, it is rejected to prevent Replay Attacks.

Recompute the Hash: The receiver concatenates the timestamp and the raw JSON body: "{timestamp}.{raw_body}". It then uses the Shared Secret to hash this string via HMAC-SHA256.

Compare Digests: The receiver compares its computed hash to the X-XInc-Signature header. If they match exactly, the payload is mathematically proven to be authentic and untampered.

🧪 Testing the Integration

To test this locally while the X-Inc worker is running:

Start this receiver (python3 app.py).

Expose your local port 8000 to the internet (using a tool like ngrok or localtunnel).

Provide that public URL to your X-Inc webhook configuration.

Upload a document to the X-Inc pipeline and watch the verified payload arrive safely in your terminal! EOF


cat << 'EOF' > examples/webhook-receiver/README.md # X-Inc AI Parser: Reference Webhook Receiver Welcome to the X-Inc Enterprise Integration kit. This directory contains a lightweight, production-ready reference implementation for receiving AI-extracted document data from the X-Inc Engine. Because we process sensitive financial documents (Purchase Orders, Invoices, etc.), our webhook delivery system enforces **Bank-Grade Cryptographic Security (HMAC-SHA256)**. This prevents replay attacks, man-in-the-middle tampering, and spoofing. ## 🚀 Quick Start This receiver is built with [FastAPI](https://fastapi.tiangolo.com/), the modern standard for high-performance Python APIs. ### 1. Install Dependencies Ensure you have Python 3.9+ installed, then install the required packages: ```bash pip install -r requirements.txt 

2. Configure Your Secret

In a production environment, you must securely store the shared secret provided by your X-Inc account manager. For this local test, it defaults to xinc-dev-secret-2026.

3. Run the Server

Start the local FastAPI server:

Bash

python3 app.py 

The server will start listening on http://0.0.0.0:8000/webhooks/x-inc.

🛡️ Security Architecture: How It Works

When the X-Inc AI Parser finishes extracting a document, it sends an HTTP POST request to your endpoint. We utilize the CloudEvents 1.0 specification.

Every request includes two critical security headers:

X-XInc-Timestamp: The exact Unix timestamp when the event was fired.

X-XInc-Signature: The cryptographic hash proving authenticity.

The Verification Process

Your receiver must perform three checks before accepting the data (all demonstrated in app.py):

Timestamp Validation: The receiver checks if Current_Time - X-XInc-Timestamp > 300 seconds. If the payload is older than 5 minutes, it is rejected to prevent Replay Attacks.

Recompute the Hash: The receiver concatenates the timestamp and the raw JSON body: "{timestamp}.{raw_body}". It then uses the Shared Secret to hash this string via HMAC-SHA256.

Compare Digests: The receiver compares its computed hash to the X-XInc-Signature header. If they match exactly, the payload is mathematically proven to be authentic and untampered.

🧪 Testing the Integration

To test this locally while the X-Inc worker is running:

Start this receiver (python3 app.py).

Expose your local port 8000 to the internet (using a tool like ngrok or localtunnel).

Provide that public URL to your X-Inc webhook configuration.

Upload a document to the X-Inc pipeline and watch the verified payload arrive safely in your terminal!

