import json
import os
import subprocess
import sys
from pathlib import Path

from test_receipt_lint import make_receipt, write_receipt


CLI_ENV = {**os.environ, "PYTHONPATH": str(Path(__file__).parents[1] / "src")}


def test_cli_returns_zero_for_valid_receipt(tmp_path):
    receipt = write_receipt(tmp_path, make_receipt(tmp_path))
    result = subprocess.run(
        [sys.executable, "-m", "receiptproof.cli", str(receipt), "--root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
        env=CLI_ENV,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["artifact"]["path"] == "dist/report.txt"


def test_cli_returns_nonzero_for_invalid_receipt(tmp_path):
    payload = make_receipt(tmp_path, exit_code=3)
    receipt = write_receipt(tmp_path, payload)
    result = subprocess.run(
        [sys.executable, "-m", "receiptproof.cli", str(receipt), "--root", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
        env=CLI_ENV,
    )
    assert result.returncode == 1
    assert "exit_code must be 0" in result.stderr
