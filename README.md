# hERG-Guard — Rule-based Audit Demonstrator

A small Python and browser-based demonstration of deterministic input validation, threshold alerts, API responses, and an in-process HMAC audit ledger.

**Scientific scope:** Despite the repository name, this is **not a validated hERG cardiotoxicity prediction model**. It does not process SMILES, calculate hERG IC50, estimate QTc prolongation or torsades de pointes probability, or implement a trained QSAR/ML model. Its numeric thresholds have arbitrary units and are **not** ICH S7B/E14 clinical or preclinical safety cutoffs. Do not use the outputs for clinical care, compound selection, or experimental safety decisions.

## Browser demonstration

Open [web/index.html](web/index.html) directly in a modern browser. The interface computes locally, shows rule-triggered alerts and session counts, and exports the last result as JSON. No backend, network connection, account, or key is required. The GitHub Pages deployment workflow publishes this directory when Pages is enabled for the repository.

The browser reflects the `agents/` demonstration rules: primary metric **>25**, secondary metric **>12**, a manual critical flag, and configured anomaly keywords in the status descriptor. These rules do not represent pharmacological decision thresholds.

## Installation

Python 3.9 or later is supported by package metadata; CI runs on Python 3.10–3.12.

```bash
git clone https://github.com/abusuraihsakhri/herg-cardiotoxicity-predictor.git
cd herg-cardiotoxicity-predictor
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[server,test]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

In Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and set the key through `$env:AUDIT_SECRET_KEY = "..."`.

## Python workflows

The repository maintains two related, but distinct, deterministic engines:

| Workflow | Entry point | Secondary demo threshold | Audit ledger |
| --- | --- | --- | --- |
| General worker audit | `python cli.py` or `herg-audit` | >12 | In-process HMAC chain |
| Alternative hERG-Guard audit | `python -m herg_guard.cli` or `herg-cardiotoxicity-predictor` | >10 | In-memory task registry only |

Both use a primary metric threshold of >25 and a manual critical flag. Their classifications must not be interpreted as hERG channel blockade predictions. The alternate engine has additional descriptor keywords. See the corresponding source files for authoritative rules.

```bash
python cli.py audit --task-id TASK-001 --target SAMPLE-01 --primary 28.5 --secondary 14.2 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py chat "What is the status?"
python cli.py serve --host 127.0.0.1 --port 8000
python -m herg_guard.cli audit --primary 29 --secondary 14
python -m pytest -q
```

The general FastAPI application is available at `http://127.0.0.1:8000/docs`. Its principal endpoints are `GET /health`, `POST /api/audit`, `POST /api/chat`, `GET /metrics` (JSON summary), and `GET /api/audit/logs`. The alternative app can be created with `herg_guard.server.create_app()`. The server requires a Python-capable host; GitHub Pages publishes only the static browser demonstration.

## Privacy and audit security

- The browser runs the rule evaluation entirely on-device and does not send, sign, or persist entered data. Do not enter patient identifiers.
- The Python general engine uses regex-based checks for certain identifiable text patterns; **these checks do not establish de-identification or HIPAA compliance**.
- The general-engine audit chain signs record metadata with HMAC-SHA256 using `AUDIT_SECRET_KEY` (minimum 16 characters). It is **in process only**, not durable or externally anchored; restarting the process clears the ledger. `verify-audit` checks the ledger in the current process and cannot verify a previous run.
- To access `GET /api/audit/logs`, set a separate `AUDIT_LOG_API_KEY` environment variable and pass the same value in the `X-Audit-Log-Key` header. Without configuration the endpoint responds 503, and unauthenticated requests are rejected.
- The chat adapter is a deterministic mock. No remote LLM services are implemented.
- The API is intended for local or otherwise trusted environments. Do not expose it publicly without appropriate authentication, TLS, rate limiting and access restrictions.

## Docker

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

Compose binds the API to `127.0.0.1:8000` by default so it is not exposed on public network interfaces. The API's audit-log key is optional and must be explicitly configured if access to audit logs is required.

## Technology and compatibility

Python standard library, Pydantic 2, FastAPI and Uvicorn (optional server dependencies); browser interface built with plain HTML, CSS, and JavaScript. A recent Chrome, Edge, Firefox, or Safari browser is recommended. The CI workflow tests the Python package and checks browser JavaScript syntax with Node.js.

## License

[MIT](LICENSE).
