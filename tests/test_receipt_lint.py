import hashlib
import json
from pathlib import Path

import pytest

from receiptproof import ReceiptError, verify_receipt


def make_receipt(root: Path, *, path="dist/report.txt", **overrides):
    artifact = root / path
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("verified artifact\n", encoding="utf-8")
    payload = {
        "schema_version": 1,
        "receipt_id": "run-2026-09-20T120000Z",
        "code_sha": "a" * 40,
        "command": "pytest -q",
        "exit_code": 0,
        "artifact": {
            "path": path,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "bytes": artifact.stat().st_size,
        },
        "recorded_at": "2026-09-20T12:00:00Z",
    }
    payload.update(overrides)
    return payload


def write_receipt(tmp_path, payload):
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps(payload), encoding="utf-8")
    return receipt


def test_verify_accepts_valid_receipt_and_returns_payload(tmp_path):
    payload = make_receipt(tmp_path)
    result = verify_receipt(write_receipt(tmp_path, payload), repo_root=tmp_path)
    assert result == payload


def test_verify_rejects_artifact_hash_tampering(tmp_path):
    payload = make_receipt(tmp_path)
    (tmp_path / "dist/report.txt").write_text("tampered value!!!\n", encoding="utf-8")
    with pytest.raises(ReceiptError, match="hash mismatch"):
        verify_receipt(write_receipt(tmp_path, payload), repo_root=tmp_path)


def test_verify_rejects_artifact_path_escape(tmp_path):
    payload = make_receipt(tmp_path, path="../outside.txt")
    with pytest.raises(ReceiptError, match="escapes repo"):
        verify_receipt(write_receipt(tmp_path, payload), repo_root=tmp_path)


def test_verify_rejects_schema_extra_property(tmp_path):
    payload = make_receipt(tmp_path, unexpected="not allowed")
    with pytest.raises(ReceiptError, match="Additional properties are not allowed"):
        verify_receipt(write_receipt(tmp_path, payload), repo_root=tmp_path)


def test_verify_rejects_nonzero_command_exit(tmp_path):
    payload = make_receipt(tmp_path, exit_code=1)
    with pytest.raises(ReceiptError, match="exit_code must be 0"):
        verify_receipt(write_receipt(tmp_path, payload), repo_root=tmp_path)


def test_verify_rejects_unexpected_code_sha(tmp_path):
    payload = make_receipt(tmp_path)
    with pytest.raises(ReceiptError, match="code_sha does not match"):
        verify_receipt(
            write_receipt(tmp_path, payload),
            repo_root=tmp_path,
            expected_code_sha="b" * 40,
        )
