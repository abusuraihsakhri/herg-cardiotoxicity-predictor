"""
FastAPI REST API Server for Herg Cardiotoxicity Predictor.
"""
import hmac
import os
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Herg Cardiotoxicity Predictor API",
    description="Rule-based demonstration API; not a validated hERG, QTc or clinical risk model",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "herg-cardiotoxicity-predictor", "domain": "AI Drug Discovery, Structural Biology & Wet-Lab Robotics", "standard": "Unvalidated demonstration rule set", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a prohibited identifier") from None
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a prohibited identifier") from None


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_log_key: Optional[str] = Header(default=None)):
    expected = os.environ.get("AUDIT_LOG_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="Audit-log access is not configured")
    if not x_audit_log_key or not hmac.compare_digest(x_audit_log_key, expected):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
