"""Command-line receipt verifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .lint import ReceiptError, verify_receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="receiptproof",
        description="Validate a JSON receipt and the artifact it names.",
    )
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."), help="artifact repository root")
    parser.add_argument("--expected-code-sha", help="require this commit SHA in the receipt")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = verify_receipt(
            args.receipt,
            repo_root=args.root,
            expected_code_sha=args.expected_code_sha,
        )
    except (ReceiptError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"receiptproof: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
