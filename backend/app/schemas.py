from __future__ import annotations

from pydantic import BaseModel


class InvoicePayload(BaseModel):
    invoice_number: str | None = None
    vendor_name: str | None = None
    vendor_tax_code: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    subtotal: float | None = None
    vat_amount: float | None = None
    total_amount: float | None = None
    currency: str = "VND"
    ocr_confidence: float | None = None


class ResolvePayload(BaseModel):
    resolved: bool = True

