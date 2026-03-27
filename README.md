# 🛡️ AWS AI Parser Engine: Mobile-Hardened Edition

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=fastapi&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Termux-orange.svg)
![Architecture](https://img.shields.io/badge/Arch-Decoupled_Microservices-blueviolet.svg)
![Security](https://img.shields.io/badge/PII_Shield-Active-red.svg)

An enterprise-grade, PII-compliant document ingestion and RAG (Retrieval-Augmented Generation) engine. This system is architected to run in **constrained environments** (Termux/Android) while maintaining the structural integrity of a multi-service cloud deployment.

---

## 🏗️ Architectural Overview

The system operates as a decoupled "Black Box" mimicking a cloud-native SQS/Lambda/DynamoDB workflow.

* **Ingestion Layer (The Nervous System):** A Polling Observer monitors the \`./ingest\` directory.
* **Security Layer (The Shield):** Every document is passed through the \`SecurityGateway\` to detect and redact SSNs, Credit Cards, and Emails.
* **Sanitization Layer:** Redacted data is wrapped in a **Unified Envelope v2.0.0** and stored in \`./processed\`.
* **Retrieval Layer (The Brain):** A FastAPI-based Orchestrator provides a RAG-enabled endpoint to query the "Clean Box" storage.

---

## 📂 Directory Structure

\`\`\`text
aws-ai-parser-engine/
├── Makefile                # Master automation interface
├── README.md               # Documentation (You are here)
├── .gitignore              # Security-first file exclusion
├── ingest/                 # Input: Dirty files (SSN/PII)
├── processed/              # Output: Sanitized JSON Envelopes
├── worker.log              # Nervous system diagnostics
├── orchestrator.log        # Brain diagnostics
└── services/
    ├── common/             # Shared logic (Clients & Models)
    │   ├── bedrock_client.py
    │   ├── textract_client.py
    │   └── pydantic_models.py
    ├── extraction_worker/  # The Nervous System
    │   ├── src/
    │   │   ├── main.py             # Polling ingest logic
    │   │   └── security_gateway.py # Regex PII Redaction
    │   └── prompts/
    └── orchestration/      # The Brain
        └── src/
            ├── router.py           # FastAPI & 3.13 Patch
            └── engine_b.py         # RAG retrieval logic
\`\`\`

---

## 🧪 The Python 3.13 "Nuclear Patch"

Running modern AI stacks on Python 3.13 (Termux) currently breaks \`FastAPI\` and \`Pydantic\` due to internal changes in \`typing.ForwardRef\`. 

This project implements a **Nucleus Monkeypatch** inside \`router.py\`. By intercepting the \`ForwardRef._evaluate\` call and dynamically handling the new \`recursive_guard\` and \`type_params\` arguments, we ensure that the entire stack remains stable on bleeding-edge Python runtimes.

---

## 🛠️ Usage (The Makefile Interface)

We provide a streamlined management interface to control the entire microservice stack.

| Command | Action |
| :--- | :--- |
| **\`make reset\`** | 🧹 Wipe all test data, logs, and reset folders |
| **\`make start\`** | 🚀 Launch Worker & Orchestrator in background |
| **\`make status\`**| 📊 Check process health and queue counts |
| **\`make test\`** | 🧪 Inject a dirty file and query the API automatically |
| **\`make batch\`** | 📂 Bulk ingest a directory of documents |
| **\`make stop\`** | 🛑 Kill all running engine processes |

---

## 🛡️ Security & Redaction Logic

The \`SecurityGateway\` utilizes multi-pattern regex matching to identify and scrub high-risk PII:
* **SSN Pattern:** Standard US format detection and masking.
* **Credit Card Pattern:** Multi-vendor card numbering formats.
* **Unified Envelope:** Data is transformed from raw text into a versioned JSON schema with a unique \`trace_id\`.

---

## 💻 Tech Stack

* **Core:** Python 3.13
* **API:** FastAPI / Uvicorn
* **Automation:** GNU Make
* **Parsing:** Regex / Pydantic (Shielded)
* **Environment:** Termux (Mobile-Hardened)

---

## 📄 License
Distributed under the MIT License. See \`LICENSE\` for more information.
