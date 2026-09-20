"""Receipt schema and semantic validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).with_name("receipt.schema.json")
_VALIDATOR = Draft202012Validator(
    json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
    format_checker=FormatChecker(),
)


class ReceiptError(ValueError):
    """Receipt failed schema or semantic validation."""


def _artifact_path(repo_root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ReceiptError(f"artifact path escapes repo: {relative}")
    root = repo_root.resolve()
    target = (root / candidate).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ReceiptError(f"artifact path escapes repo: {relative}") from exc
    return target


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_receipt(path: Path, *, repo_root: Path, expected_code_sha: str | None = None) -> dict:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReceiptError(f"invalid JSON: {exc.msg}") from exc
    errors = sorted(_VALIDATOR.iter_errors(payload), key=lambda error: list(error.path))
    if errors:
        raise ReceiptError("; ".join(error.message for error in errors))
    if payload["exit_code"] != 0:
        raise ReceiptError("exit_code must be 0 for a successful receipt")
    if expected_code_sha is not None and payload["code_sha"] != expected_code_sha:
        raise ReceiptError("code_sha does not match expected code SHA")

    artifact = payload["artifact"]
    target = _artifact_path(Path(repo_root), artifact["path"])
    if not target.exists() or target.is_symlink() or not target.is_file():
        raise ReceiptError(f"artifact missing or not a regular file: {artifact['path']}")
    if target.stat().st_size != artifact["bytes"]:
        raise ReceiptError(f"artifact size mismatch: {artifact['path']}")
    if _sha256(target) != artifact["sha256"]:
        raise ReceiptError(f"artifact hash mismatch: {artifact['path']}")
    return payload
