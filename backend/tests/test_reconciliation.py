from app.services.reconciliation import calculate_match_score, classify_match
from app.services.validation import validate_invoice, validation_status


def test_exact_invoice_transaction_match_scores_high():
    invoice = {
        "invoice_number": "INV-2026-001",
        "invoice_date": "2026-06-05",
        "vendor_name": "Cong ty TNHH Minh Anh",
        "total_amount": 6050000,
    }
    transaction = {
        "transaction_date": "2026-06-07",
        "description": "Thanh toan hoa don INV-2026-001 Cong ty Minh Anh",
        "amount": 6050000,
    }

    metrics = calculate_match_score(invoice, transaction)

    assert metrics["score"] >= 85
    assert classify_match(metrics["score"], metrics["amount_diff"]) == "matched"


def test_amount_mismatch_is_classified_for_close_candidate():
    invoice = {
        "invoice_number": "INV-2026-010",
        "invoice_date": "2026-06-10",
        "vendor_name": "Sao Viet",
        "total_amount": 8800000,
    }
    transaction = {
        "transaction_date": "2026-06-12",
        "description": "CK HD INV-2026-010 CTY SAO VIET",
        "amount": 8500000,
    }

    metrics = calculate_match_score(invoice, transaction)

    assert metrics["score"] >= 60
    assert classify_match(metrics["score"], metrics["amount_diff"]) == "amount_mismatch"


def test_invoice_validation_detects_duplicate_and_total_mismatch():
    invoice = {
        "invoice_number": "INV-2026-001",
        "invoice_date": "2026-06-05",
        "vendor_name": "Unknown Vendor",
        "subtotal": 100,
        "vat_amount": 10,
        "total_amount": 90,
    }
    issues = validate_invoice(invoice, vendors=[], duplicate_count=2)

    issue_types = {issue["type"] for issue in issues}
    assert "duplicate_invoice_number" in issue_types
    assert "total_mismatch" in issue_types
    assert validation_status(issues) == "invalid"

