import os
import json
import logging

logger = logging.getLogger(__name__)

class DeepReasoningEngine:
    def __init__(self):
        self.storage_dir = "./processed" 

    def retrieve_context(self, query: str) -> str:
        logger.info(f"🔎 Engine B scanning for: {query}")
        
        if not os.path.exists(self.storage_dir):
            return "Knowledge base directory missing."

        matches = []
        files = os.listdir(self.storage_dir)
        
        if not files:
            return "Secure storage is currently empty."

        for filename in files:
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_dir, filename), 'r') as f:
                        data = json.load(f)
                        # Look inside the Unified Envelope structure
                        text = data.get("extracted_data", {}).get("sanitized_text", "")
                        
                        if query.lower() in text.lower():
                            matches.append(f"[{filename}]: {text}")
                except Exception as e:
                    logger.error(f"⚠️ Error reading {filename}: {e}")

        return " | ".join(matches) if matches else "No matching sanitized context found."

    def generate_response(self, message: str) -> dict:
        context = self.retrieve_context(message)
        return {"answer": context, "status": "success"}
