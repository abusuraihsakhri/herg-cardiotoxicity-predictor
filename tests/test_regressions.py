"""Regression checks for audit integrity, API protection and browser syntax."""
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agents.base import AuditTrail
from agents.api import app
from agents.llm_factory import LLMFactory
from herg_guard.models import FrontierPayload


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and not dict(attrs).get("src"):
            self.inside = True

    def handle_data(self, data):
        if self.inside:
            self.scripts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside = False


def test_hmac_detects_signed_field_tampering():
    ledger = AuditTrail("my-long-secret-for-integrity-tests")
    ledger.log("worker", "system", "SUBMITTED", {"count": 1})
    ledger.log("worker", "system", "COMPLETED", {"count": 2})
    assert ledger.verify_integrity()
    ledger.logs[1]["event_type"] = "MODIFIED"
    assert not ledger.verify_integrity()


def test_audit_snapshots_are_not_mutable():
    ledger = AuditTrail("my-long-secret-for-integrity-tests")
    event = ledger.log("worker", "system", "SUBMITTED", {"count": 1})
    event["event_type"] = "MODIFIED"
    snapshot = ledger.get_trail()
    snapshot[0]["current_hash"] = "FAKE"
    assert ledger.verify_integrity()


def test_api_audit_access_requires_separate_key(monkeypatch):
    client = TestClient(app)
    monkeypatch.delenv("AUDIT_LOG_API_KEY", raising=False)
    assert client.get("/api/audit/logs").status_code == 503
    monkeypatch.setenv("AUDIT_LOG_API_KEY", "only-for-tests-access-token")
    assert client.get("/api/audit/logs").status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Log-Key": "wrong"}).status_code == 403
    ok = client.get("/api/audit/logs", headers={"X-Audit-Log-Key": "only-for-tests-access-token"})
    assert ok.status_code == 200
    assert ok.json()["verified"] is True


def test_api_rejects_sensitive_descriptor_without_internal_error():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "TASK-1", "target_identifier": "TARGET-1",
        "primary_metric": 1.0, "status_descriptor": "Patient John Doe"
    })
    assert response.status_code == 422


def test_mock_does_not_claim_validated_inference():
    msg = LLMFactory.create("mock").invoke("What is the status?")
    assert "No scientific or clinical inference performed" in msg
    with pytest.raises(ValueError, match="not implemented"):
        LLMFactory.create("openai")


def test_alternate_model_rejects_boolean_and_nonfinite_inputs():
    fields = {"task_id": "T1", "target_identifier": "S1", "primary_metric": 4.0,
              "secondary_metric": 1.0, "status_descriptor": "NOMINAL"}
    for invalid in (True, float("inf"), float("nan"), 10 ** 1000):
        with pytest.raises(ValueError, match="finite"):
            FrontierPayload(**{**fields, "primary_metric": invalid})


def test_browser_has_valid_javascript():
    if not shutil.which("node"):
        pytest.skip("Node.js not installed")
    parser = Scripts()
    parser.feed((Path(__file__).parent.parent / "web" / "index.html").read_text())
    assert len(parser.scripts) == 1
    check = subprocess.run(["node", "--check"], input=parser.scripts[0], text=True,
                           capture_output=True, timeout=15, check=False)
    assert check.returncode == 0, check.stderr
