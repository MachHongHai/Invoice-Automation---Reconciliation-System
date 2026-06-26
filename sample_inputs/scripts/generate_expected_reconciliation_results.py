from __future__ import annotations

from generation_core import (
    ensure_directories,
    generate_bank_statement,
    generate_expected_reconciliation_results,
    generate_invoice_register,
    generate_payment_batch,
    generate_vendors,
)


def main() -> None:
    ensure_directories()
    vendors = generate_vendors()
    invoices = generate_invoice_register(vendors)
    payments = generate_payment_batch(invoices)
    transactions = generate_bank_statement(invoices, payments, vendors)
    rows = generate_expected_reconciliation_results(invoices, payments, transactions)
    print(f"Generated expected reconciliation rows: {len(rows)}")


if __name__ == "__main__":
    main()
