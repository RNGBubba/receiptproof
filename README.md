# ReceiptProof

ReceiptProof is a small, dependency-light CLI for validating JSON execution receipts and the artifacts they name. It combines strict JSON Schema validation with semantic checks that a shape-only validator cannot provide.

## What it checks

- required fields and closed objects (`additionalProperties: false`)
- SHA-1-style Git commit identifiers (40 or 64 lowercase hex characters)
- ISO 8601 `recorded_at` timestamps
- successful command completion (`exit_code == 0`)
- artifact paths that remain inside the selected repository root
- regular, non-symlink artifact files
- exact artifact byte count and SHA-256 digest
- optional expected code SHA

## Usage

```bash
python -m pip install -e .
receiptproof receipt.json --root .
receiptproof receipt.json --root . --expected-code-sha "$GIT_COMMIT_SHA"
```

The command prints the validated receipt to stdout and exits nonzero with a diagnostic when validation fails.

## Receipt shape

See `src/receiptproof/receipt.schema.json`. A receipt must include `schema_version`, `receipt_id`, `code_sha`, `command`, `exit_code`, `artifact`, and `recorded_at`. The artifact object contains a repository-relative `path`, a SHA-256 `sha256`, and positive `bytes`.

## Development

```bash
uv sync
uv run pytest -q
```

This project is original work and is not affiliated with DoneMeans or any other receipt system.
