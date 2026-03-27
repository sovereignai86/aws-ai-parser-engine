#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.

echo "🚀 Starting X-Inc AI Parser Stack..."

# 1. Start the Worker (Nervous System)
nohup python3 -m services.extraction_worker.src.main > worker.log 2>&1 &
echo "  [OK] Extraction Worker online."

# 2. Start the Orchestrator (The Brain)
# Running in background so the script returns control to you
nohup python3 -m services.orchestration.src.router > orchestrator.log 2>&1 &
echo "  [OK] Orchestrator online on port 8080."

echo "------------------------------------------------"
echo "✅ System ready. Drop files into ./ingest/"
echo "🔍 Query the API: curl http://localhost:8080/health"
echo "------------------------------------------------"
