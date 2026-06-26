from __future__ import annotations

from datetime import date
from difflib import SequenceMatcher
from typing import Any

from app.utils import normalize_text, parse_date


def fuzzy_similarity(left: str | None, right: str | None) -> float:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm in right_norm or right_norm in left_norm:
        return 100.0
    return SequenceMatcher(None, left_norm, right_norm).ratio() * 100


def vendor_exists(invoice: dict[str, Any], vendors: list[dict[str, Any]]) -> bool:
    tax_code = normalize_text(invoice.get("vendor_tax_code"))
    vendor_name = normalize_text(invoice.get("vendor_name"))
    for vendor in vendors:
        if tax_code and tax_code == normalize_text(vendor.get("tax_code")):
            return True
        if vendor_name and fuzzy_similarity(vendor_name, vendor.get("vendor_name")) >= 82:
            return True
    return False


def validate_invoice(
    invoice: dict[str, Any],
    vendors: list[dict[str, Any]],
    duplicate_count: int = 1,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    if not invoice.get("invoice_number"):
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "medium",
                "message": "Invoice number is missing.",
            }
        )

    invoice_date = parse_date(invoice.get("invoice_date"))
    if not invoice_date:
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "medium",
                "message": "Invoice date is missing or invalid.",
            }
        )
    elif invoice_date > date.today().isoformat():
        issues.append(
            {
                "type": "date_mismatch",
                "severity": "medium",
                "message": "Invoice date is in the future.",
            }
        )

    total = invoice.get("total_amount")
    subtotal = invoice.get("subtotal")
    vat = invoice.get("vat_amount")

    if total is None or float(total or 0) <= 0:
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "high",
                "message": "Total amount must be greater than zero.",
            }
        )

    if vat is not None and float(vat) < 0:
        issues.append(
            {
                "type": "amount_mismatch",
                "severity": "high",
                "message": "VAT amount cannot be negative.",
            }
        )

    if subtotal is not None and vat is not None and total is not None:
        diff = abs((float(subtotal) + float(vat)) - float(total))
        if diff > 1:
            issues.append(
                {
                    "type": "amount_mismatch",
                    "severity": "high",
                    "message": f"Subtotal plus VAT differs from total by {diff:,.0f}.",
                }
            )

    if vendors and not vendor_exists(invoice, vendors):
        issues.append(
            {
                "type": "vendor_mismatch",
                "severity": "medium",
                "message": "Vendor does not exist in vendor master.",
            }
        )

    if invoice.get("invoice_number") and duplicate_count > 1:
        issues.append(
            {
                "type": "duplicate_invoice",
                "severity": "critical",
                "message": "Invoice number appears more than once.",
            }
        )

    confidence = invoice.get("ocr_confidence")
    if confidence is not None and float(confidence) < 80:
        issues.append(
            {
                "type": "low_ocr_confidence",
                "severity": "low",
                "message": f"OCR confidence is {float(confidence):.1f}%, below the 80% review threshold.",
            }
        )

    return issues


def validation_status(issues: list[dict[str, str]]) -> str:
    if not issues:
        return "valid"
    if any(issue["severity"] in {"critical", "high"} for issue in issues):
        return "invalid"
    return "needs_review"


def validate_bank_transaction(
    transaction: dict[str, Any],
    duplicate_count: int = 1,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    if not transaction.get("transaction_id"):
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "high",
                "message": "Transaction ID is missing.",
            }
        )
    elif duplicate_count > 1:
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "high",
                "message": "Transaction ID appears more than once.",
            }
        )

    if not parse_date(transaction.get("transaction_date")):
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "high",
                "message": "Transaction date is missing or invalid.",
            }
        )

    amount = transaction.get("amount")
    if amount is None or float(amount or 0) == 0:
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "high",
                "message": "Transaction amount must be non-zero.",
            }
        )

    direction = (transaction.get("direction") or "").lower()
    if direction not in {"inflow", "outflow"}:
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "high",
                "message": "Transaction direction must be inflow or outflow.",
            }
        )

    if not transaction.get("description"):
        issues.append(
            {
                "type": "missing_required_field",
                "severity": "low",
                "message": "Transaction description is empty.",
            }
        )

    return issues
