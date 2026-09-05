"""
Pytest configuration — sets required environment variables for tests.
"""
import os
import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set a deterministic audit secret key for the test environment
os.environ.setdefault("AUDIT_SECRET_KEY", "test-audit-secret-key-for-pytest-2026")
