from __future__ import annotations

from generation_core import ensure_directories, generate_invoices, generate_vendors


if __name__ == "__main__":
    ensure_directories()
    vendors = generate_vendors()
    invoices, items = generate_invoices(vendors)
    print(f"Generated invoices: {len(invoices)}")
    print(f"Generated invoice items: {len(items)}")

