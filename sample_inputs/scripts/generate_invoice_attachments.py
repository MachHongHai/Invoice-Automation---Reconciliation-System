from __future__ import annotations

from generation_core import ensure_directories, generate_invoice_attachments, generate_invoice_register, generate_vendors


def main() -> None:
    ensure_directories()
    vendors = generate_vendors()
    invoices = generate_invoice_register(vendors)
    paths = generate_invoice_attachments(invoices)
    print(f"Generated invoice PDF attachments: {len(paths)}")


if __name__ == "__main__":
    main()
