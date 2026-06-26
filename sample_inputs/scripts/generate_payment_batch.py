from __future__ import annotations

from generation_core import ensure_directories, generate_invoice_register, generate_payment_batch, generate_vendors


def main() -> None:
    ensure_directories()
    vendors = generate_vendors()
    invoices = generate_invoice_register(vendors)
    payments = generate_payment_batch(invoices)
    print(f"Generated payment batch rows: {len(payments)}")


if __name__ == "__main__":
    main()
