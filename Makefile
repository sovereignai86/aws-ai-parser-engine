# --- Global Configuration ---
PYTHON = python3
PYTHONPATH = .
INGEST_DIR = ingest
PROCESSED_DIR = processed

# Service Modules
WORKER_MODULE = services.extraction_worker.src.main
ORCHESTRATOR_MODULE = services.orchestration.src.router

.PHONY: help start stop restart reset status logs test batch

help:
	@echo "🛠️  AWS AI Parser Engine - Mobile Edition"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  start      🚀 Launch Worker & Orchestrator in background"
	@echo "  stop       🛑 Kill all running engine processes"
	@echo "  restart    ♻️  Full stop and clean start"
	@echo "  reset      🧹 Wipe all test data, logs, and reset folders"
	@echo "  status     📊 Check process health and file counts"
	@echo "  logs       📜 Tail the output of both services"
	@echo "  test       🧪 Inject a single dirty file and query the API"
	@echo "  batch      📂 Bulk ingest files from a source directory"

# --- Core Operations ---

start:
	@mkdir -p $(INGEST_DIR) $(PROCESSED_DIR)
	@echo "🚀 Launching Nervous System (Worker)..."
	@export PYTHONPATH=$(PYTHONPATH) && nohup $(PYTHON) -m $(WORKER_MODULE) > worker.log 2>&1 &
	@echo "🚀 Launching Brain (Orchestrator)..."
	@export PYTHONPATH=$(PYTHONPATH) && nohup $(PYTHON) -m $(ORCHESTRATOR_MODULE) > orchestrator.log 2>&1 &
	@echo "✅ System online. API listening on port 8080."

stop:
	@echo "🛑 Stopping Python processes..."
	@pkill -f "$(WORKER_MODULE)" || true
	@pkill -f "$(ORCHESTRATOR_MODULE)" || true
	@pkill -f "python3" || true
	@echo "💤 System offline."

restart: stop start

reset: stop
	@echo "🧹 Ground Zero Reset..."
	@rm -rf $(INGEST_DIR)/* $(PROCESSED_DIR)/* worker.log orchestrator.log
	@mkdir -p $(INGEST_DIR) $(PROCESSED_DIR)
	@echo "✨ Folders cleared. System reset."

# --- Monitoring & Batch ---

status:
	@echo "------------------------------------------------"
	@echo "📊 SYSTEM STATUS"
	@echo "------------------------------------------------"
	@pgrep -fl "$(WORKER_MODULE)" && echo "🟢 Worker:       RUNNING" || echo "🔴 Worker:       DOWN"
	@pgrep -fl "$(ORCHESTRATOR_MODULE)" && echo "🟢 Orchestrator: RUNNING" || echo "🔴 Orchestrator: DOWN"
	@echo ""
	@echo "📥 Ingest Queue:   $$(ls -1 $(INGEST_DIR) 2>/dev/null | wc -l) files"
	@echo "✅ Processed Bank: $$(ls -1 $(PROCESSED_DIR) 2>/dev/null | wc -l) envelopes"
	@echo "------------------------------------------------"

batch:
	@read -p "📂 Enter absolute path to source directory: " src_path; \
	if [ -d "$$src_path" ]; then \
		echo "🚚 Moving files from $$src_path to $(INGEST_DIR)..."; \
		cp -v "$$src_path"/* $(INGEST_DIR)/; \
		echo "✅ Batch transfer complete. Monitoring for redaction..."; \
	else \
		echo "❌ Error: Directory $$src_path not found."; \
	fi

logs:
	@echo "📜 Tailing logs (Ctrl+C to stop)..."
	@tail -f worker.log -f orchestrator.log

test:
	@echo "🧪 Injecting dirty PII data..."
	@echo "Invoice for John Doe, SSN: 123-45-6789, CC: 4444-5555-6666-7777" > $(INGEST_DIR)/dirty_invoice.txt
	@echo "⏳ Waiting for security redaction..."
	@sleep 4
	@echo "🔍 Querying the RAG API..."
	@curl -s "http://localhost:8080/api/v1/rag/retrieve?query=John%20Doe" | python3 -m json.tool
