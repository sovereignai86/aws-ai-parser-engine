import sys

# --- 🧪 THE NUCLEAR COMPATIBILITY PATCH (Python 3.13 Fix) ---
# This MUST happen before 'import fastapi' or 'import pydantic'
if sys.version_info >= (3, 13):
    import typing
    from typing import ForwardRef
    
    # Python 3.13 changed the _evaluate signature. 
    # This patch makes it backward compatible with Pydantic 1.10.
    real_evaluate = ForwardRef._evaluate
    
    def patched_evaluate(self, globalns, localns, *args, **kwargs):
        # If 'recursive_guard' isn't in kwargs, add it to satisfy 3.13
        if 'recursive_guard' not in kwargs:
            kwargs['recursive_guard'] = frozenset()
        return real_evaluate(self, globalns, localns, *args, **kwargs)
    
    ForwardRef._evaluate = patched_evaluate

# Now we can safely import the rest of the stack
import os
import time
import logging
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
import uvicorn

# --- PATH INJECTION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.orchestration.src.engine_b import DeepReasoningEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ORCHESTRATOR] - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="X-Inc AI Parser (3.13 Shielded)")
engine_b = DeepReasoningEngine()

@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "Engine B Online"}

@app.get("/api/v1/rag/retrieve")
async def manual_retrieve(query: str):
    logger.info(f"🔍 Retrieval: {query}")
    context = engine_b.retrieve_context(query)
    return {
        "trace_id": str(uuid.uuid4()),
        "retrieved_context": context,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Shielded Orchestrator on http://0.0.0.0:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
