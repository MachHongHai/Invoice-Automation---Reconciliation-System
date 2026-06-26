from app.services.reconciliation import calculate_match_score, classify_match, is_reconciliation_candidate
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
        "amount": 8799000,
    }

    metrics = calculate_match_score(invoice, transaction)

    assert metrics["score"] >= 85
    assert classify_match(metrics["score"], metrics["amount_diff"]) == "amount_mismatch"
    assert is_reconciliation_candidate(invoice, transaction)


def test_candidate_selection_rejects_large_amount_or_date_gap():
    invoice = {
        "invoice_number": "INV-2026-011",
        "invoice_date": "2026-06-01",
        "vendor_name": "Minh Anh",
        "total_amount": 1000000,
    }
    far_transaction = {
        "transaction_date": "2026-07-15",
        "description": "INV-2026-011 Minh Anh",
        "amount": 1000000,
        "direction": "outflow",
    }
    large_diff_transaction = {
        "transaction_date": "2026-06-02",
        "description": "INV-2026-011 Minh Anh",
        "amount": 2000000,
        "direction": "outflow",
    }

    assert not is_reconciliation_candidate(invoice, far_transaction)
    assert not is_reconciliation_candidate(invoice, large_diff_transaction)


def test_classification_uses_configured_thresholds():
    rules = {"auto_match_threshold": 90, "manual_review_threshold": 70}

    assert classify_match(86, 0, rules) == "partially_matched"
    assert classify_match(91, 25000, rules) == "amount_mismatch"


def test_candidate_selection_uses_configured_tolerance():
    invoice = {
        "invoice_number": "INV-2026-012",
        "invoice_date": "2026-06-01",
        "vendor_name": "Cong ty Minh Anh",
        "total_amount": 1000000,
    }
    transaction = {
        "transaction_date": "2026-06-20",
        "description": "Thanh toan Cong ty Minh Anh",
        "amount": 1100000,
        "direction": "outflow",
    }

    assert is_reconciliation_candidate(invoice, transaction)
    assert not is_reconciliation_candidate(
        invoice,
        transaction,
        {"date_tolerance_days": 10, "amount_tolerance_vnd": 500000},
    )


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
    assert "duplicate_invoice" in issue_types
    assert "amount_mismatch" in issue_types
    assert validation_status(issues) == "invalid"
