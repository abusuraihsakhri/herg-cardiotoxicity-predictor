"""
Security & Input Validation Tests for herg-cardiotoxicity-predictor.
"""
import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, SecurityException, AuditTrail
from agents.models import SystemTaskPayload


class TestPHIGuardEnhancements:
    """Tests for the Zero-PHI outbound guard."""

    def test_email_pattern_matches_standard_address(self):
        """Email regex must match standard email addresses (fixed [A-Z|a-z] bug)."""
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact user@example.com for details")

    def test_clean_text_without_phi_passes(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 nominal parameters")

    def test_ssn_pattern_detected(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN 123-45-6789 submitted")

    def test_mrn_pattern_detected(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("MRN-994827 blood culture positive")

    def test_phone_pattern_detected(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567 for results")

    def test_redact_phi_replaces_sensitive_data(self):
        redacted = PHIGuard.redact_phi("Contact user@example.com or MRN-12345")
        assert "@" not in redacted
        assert "MRN-" not in redacted
        assert "[REDACTED_IDENTIFIER]" in redacted

    def test_empty_string_passes(self):
        PHIGuard.assert_no_phi("")

    def test_none_input_handled(self):
        PHIGuard.assert_no_phi(None)


class TestAuditTrailSecurity:
    """Tests for HMAC-SHA256 audit trail security requirements."""

    def test_audit_trail_requires_secret_key(self):
        """AuditTrail must not initialize without a secret key."""
        original = os.environ.get("AUDIT_SECRET_KEY")
        try:
            os.environ.pop("AUDIT_SECRET_KEY", None)
            with pytest.raises(SecurityException, match="AUDIT_SECRET_KEY"):
                AuditTrail(secret_key=None)
        finally:
            if original is not None:
                os.environ["AUDIT_SECRET_KEY"] = original

    def test_audit_trail_rejects_short_key(self):
        with pytest.raises(SecurityException, match="at least 16"):
            AuditTrail(secret_key="short")

    def test_audit_trail_accepts_valid_key(self):
        trail = AuditTrail(secret_key="this-is-a-valid-test-key")
        assert len(trail.get_trail()) == 0

    def test_audit_trail_chaining_integrity(self):
        trail = AuditTrail(secret_key="test-key-for-integrity-checks-abc")
        trail.log("actor1", "tier1", "EVENT_1", {"a": 1})
        trail.log("actor2", "tier2", "EVENT_2", {"b": 2})
        trail.log("actor3", "tier3", "EVENT_3", {"c": 3})
        assert trail.verify_integrity() is True
        assert len(trail.get_trail()) == 3

    def test_audit_trail_tamper_detection(self):
        trail = AuditTrail(secret_key="test-key-for-tamper-detection")
        trail.log("actor1", "tier1", "EVENT_1", {"a": 1})
        trail.log("actor2", "tier2", "EVENT_2", {"b": 2})
        assert trail.verify_integrity() is True
        # Simulate tampering
        trail.logs[0]["current_hash"] = "TAMPERED_HASH"
        assert trail.verify_integrity() is False


class TestInputValidation:
    """Tests for SystemTaskPayload input validation."""

    def test_valid_payload(self):
        p = SystemTaskPayload(
            task_id="TASK-001",
            target_identifier="KEY-001",
            primary_metric=15.0,
            secondary_metric=5.0,
        )
        assert p.task_id == "TASK-001"
        assert p.primary_metric == 15.0

    def test_nan_metric_rejected(self):
        with pytest.raises(ValueError, match="finite number"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("nan"))

    def test_infinity_metric_rejected(self):
        with pytest.raises(ValueError, match="finite number"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("inf"))

    def test_negative_infinity_rejected(self):
        with pytest.raises(ValueError, match="finite number"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", secondary_metric=float("-inf"))

    def test_empty_task_id_rejected(self):
        with pytest.raises(ValueError, match="non-empty string"):
            SystemTaskPayload(task_id="", target_identifier="K1", primary_metric=1.0)

    def test_invalid_characters_in_task_id_rejected(self):
        with pytest.raises(Exception) as exc_info:
            SystemTaskPayload(task_id="task id with spaces!", target_identifier="K1", primary_metric=1.0)
        assert "alphanumeric" in str(exc_info.value)

    def test_path_traversal_in_task_id_rejected(self):
        with pytest.raises(Exception) as exc_info:
            SystemTaskPayload(task_id="../../../etc/passwd", target_identifier="K1", primary_metric=1.0)
        # "../" starts with "." which is not alphanumeric, so it fails the first-char check
        assert "alphanumeric" in str(exc_info.value) or "must start" in str(exc_info.value)

    def test_valid_hyphenated_task_id(self):
        p = SystemTaskPayload(task_id="TASK-2026-001", target_identifier="KEY-001", primary_metric=10.0)
        assert p.task_id == "TASK-2026-001"

    def test_valid_dotted_target(self):
        p = SystemTaskPayload(task_id="T1", target_identifier="TARGET.KEY.001", primary_metric=10.0)
        assert p.target_identifier == "TARGET.KEY.001"


# Need os for the audit trail test that manipulates env vars
import os
