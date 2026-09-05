"""
Data Models & Telemetry Definitions for hERG-Guard: Voltage-Gated Potassium Channel Blockade & QTc Arrhythmia Agent.
Domain: Computational Chemistry & AI Drug Discovery
Standard: ICH S7B / E14 Non-Clinical Cardiac Safety
"""
import datetime
import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class ExecutionStatus(str, Enum):
    NOMINAL = "NOMINAL_OPTIMAL"
    ELEVATED_RISK = "ELEVATED_RISK_WARNING"
    CRITICAL_INTERVENTION = "CRITICAL_INTERVENTION_REQUIRED"


_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._\-]{0,127}$")


def _validate_payload_inputs(task_id: str, target_identifier: str, primary_metric: float, secondary_metric: float) -> None:
    """Validate inputs before constructing a FrontierPayload."""
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id must be a non-empty string")
    if not _IDENTIFIER_RE.match(task_id):
        raise ValueError("task_id contains invalid characters")
    if not isinstance(target_identifier, str) or not target_identifier.strip():
        raise ValueError("target_identifier must be a non-empty string")
    if not _IDENTIFIER_RE.match(target_identifier):
        raise ValueError("target_identifier contains invalid characters")
    if not isinstance(primary_metric, (int, float)) or math.isnan(primary_metric) or math.isinf(primary_metric):
        raise ValueError("primary_metric must be a finite number")
    if not isinstance(secondary_metric, (int, float)) or math.isnan(secondary_metric) or math.isinf(secondary_metric):
        raise ValueError("secondary_metric must be a finite number")


@dataclass
class FrontierPayload:
    task_id: str
    target_identifier: str
    primary_metric: float
    secondary_metric: float
    status_descriptor: str
    is_critical_flag: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def __post_init__(self):
        _validate_payload_inputs(self.task_id, self.target_identifier, self.primary_metric, self.secondary_metric)


@dataclass
class AgentTelemetryAlert:
    alert_id: str
    origin_agent: str
    status: ExecutionStatus
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "ICH S7B / E14 Non-Clinical Cardiac Safety"
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "origin_agent": self.origin_agent,
            "status": self.status.value,
            "summary": self.summary,
            "technical_details": self.technical_details,
            "actionable_remediation": self.actionable_remediation,
            "standard_reference": self.standard_reference,
            "timestamp": self.timestamp,
        }
