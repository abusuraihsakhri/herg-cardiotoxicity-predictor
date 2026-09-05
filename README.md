# Herg Cardiotoxicity Predictor

> **Domain:** Computational Biology & AI Drug Discovery
> **Reference Guidelines & Standards:** `wwPDB, IUPAC & CLSI Computational Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Herg Cardiotoxicity Predictor** is an analytical and computational platform implementing hERG potassium channel IC50 and drug-induced Torsades de Pointes arrhythmia agent evaluation.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED, CRITICAL_STAT) with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking, NaN/Infinity rejection, and anomaly detection.
- **Multi-Worker Evaluation**: InvariantQC, SafetyEscalation, and ProtocolConformance workers assess task payloads.

---

## 🚀 Quickstart

### Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/herg-cardiotoxicity-predictor.git
cd herg-cardiotoxicity-predictor

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

### Environment Variables

The following environment variable is **required** for the audit trail:

```bash
export AUDIT_SECRET_KEY="your-secure-random-key-min-16-chars"
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Chat with Supervisor
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task identifier (alphanumeric, dots, hyphens, underscores)
- `--target`: Target entity identifier
- `--primary`: Primary measurement value (finite number)
- `--secondary`: Secondary measurement value (finite number)
- `--critical`: Emergency escalation flag (boolean)
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT, ANOMALY)

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition. Requires a secret key via `AUDIT_SECRET_KEY`.
* **Input Validation:** All identifiers validated against injection patterns; metrics validated as finite numbers (NaN/Infinity rejected).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
# Set audit key for tests (or rely on conftest.py default)
export AUDIT_SECRET_KEY="test-audit-secret-key-for-pytest-2026"
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
export AUDIT_SECRET_KEY="simulation-key-min-16-chars"
python simulator.py 1000
```

### Test Coverage
- **PHI Guard Enforcement:** Email, SSN, MRN, phone, and patient name detection/redaction
- **Audit Trail Integrity:** HMAC-SHA256 chaining, tamper detection, key validation
- **Input Validation:** NaN/Infinity rejection, identifier format enforcement, path traversal prevention
- **Worker Evaluation:** Multi-worker alert generation and escalation logic
- **CLI Commands:** audit, chat, batch, verify-audit, serve

---

## 🐳 Container Deployment

Create a `.env` file with your secret key:
```
AUDIT_SECRET_KEY=your-production-secret-key-here
```

```bash
docker compose up --build
```

Or manual Docker:
```bash
docker build -t herg-cardiotoxicity-predictor .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key herg-cardiotoxicity-predictor
```

---

## 📁 Project Structure

```
herg-cardiotoxicity-predictor/
├── agents/                  # Core analytical agents module
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # PHI guard, HMAC audit trail
│   ├── models.py           # Pydantic v2 schemas with validation
│   ├── supervisor.py       # Multi-worker orchestrator
│   ├── workers.py          # Domain worker agents
│   ├── llm_factory.py      # LLM provider abstraction
│   ├── metrics.py          # Prometheus metrics collector
│   ├── learning.py         # Bayesian calibration engine
│   └── streamer.py         # WebSocket telemetry broadcaster
├── herg_guard/             # Alternative domain module
│   ├── agents.py           # hERG-Guard coordination agents
│   ├── engine.py           # Core algorithmic engine
│   ├── models.py           # Frontier payload models
│   ├── cli.py              # Domain-specific CLI
│   └── server.py           # Domain-specific FastAPI server
├── tests/                  # Pytest test suite
├── web/index.html          # Operations console UI
├── cli.py                  # Main CLI entry point
├── simulator.py            # High-throughput simulator
├── enrichment.py           # Feature enrichment modules
├── pyproject.toml          # Project metadata & dependencies
├── Dockerfile              # Container image definition
└── docker-compose.yml      # Container orchestration
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
