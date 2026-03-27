import os
import sys
import time
import json
import uuid
import logging

# Ensure absolute paths for Termux
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from services.extraction_worker.src.security_gateway import security_shield

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [WORKER] - %(message)s')
logger = logging.getLogger(__name__)

INGEST_DIR = os.path.join(project_root, "ingest")
PROCESSED_DIR = os.path.join(project_root, "processed")
os.makedirs(INGEST_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def process_file(file_path):
    if file_path.endswith(".json") or os.path.basename(file_path).startswith("."):
        return

    logger.info(f"🛡️ Security Gateway: Scanning {os.path.basename(file_path)}...")
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # PII Redaction logic
        safe_text = security_shield.redact_pii(content)
        
        envelope = {
            "envelope_version": "2.0.0",
            "trace_id": str(uuid.uuid4()),
            "extracted_data": {"sanitized_text": safe_text},
            "timestamp": time.time()
        }

        # Save to processed folder
        output_name = os.path.basename(file_path) + ".json"
        with open(os.path.join(PROCESSED_DIR, output_name), 'w') as f:
            json.dump(envelope, f)
            
        logger.info(f"✅ SUCCESS: {output_name} created in /processed")
    except Exception as e:
        logger.error(f"❌ CRASH during processing: {e}")

if __name__ == "__main__":
    logger.info(f"🚀 Shielded Worker Online (POLLING MODE). Watching: {INGEST_DIR}")
    
    # Manual Polling Loop (Most stable for Termux/Android)
    processed_cache = set()
    while True:
        try:
            current_files = set(os.listdir(INGEST_DIR))
            new_files = current_files - processed_cache
            
            for filename in new_files:
                if not filename.endswith(".json"):
                    process_file(os.path.join(INGEST_DIR, filename))
                    processed_cache.add(filename)
            
            time.sleep(2) # Poll every 2 seconds
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"System Error: {e}")
            time.sleep(5)
