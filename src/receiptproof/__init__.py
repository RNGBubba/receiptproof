"""Strict validation for artifact receipts."""

from .lint import ReceiptError, verify_receipt

__all__ = ["ReceiptError", "verify_receipt"]
