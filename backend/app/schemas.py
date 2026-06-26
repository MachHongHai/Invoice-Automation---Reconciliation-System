from __future__ import annotations

from pydantic import BaseModel


class InvoicePayload(BaseModel):
    invoice_number: str | None = None
    vendor_name: str | None = None
    vendor_tax_code: str | None = None
    vendor_bank_account: str | None = None
    vendor_address: str | None = None
    vendor_phone: str | None = None
    buyer_name: str | None = None
    buyer_tax_code: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    subtotal: float | None = None
    vat_amount: float | None = None
    total_amount: float | None = None
    currency: str = "VND"
    ocr_confidence: float | None = None


class ResolvePayload(BaseModel):
    resolved: bool = True


class LoginPayload(BaseModel):
    email: str
    password: str


class ReviewInvoicePayload(InvoicePayload):
    status: str | None = None


class ExceptionUpdatePayload(BaseModel):
    status: str | None = None
    note: str | None = None
    resolved: bool | None = None


class RulePayload(BaseModel):
    auto_match_threshold: float = 85
    manual_review_threshold: float = 60
    date_tolerance_days: int = 30
    amount_tolerance_vnd: float = 500000
    low_ocr_confidence_threshold: float = 80
    vat_tolerance: float = 1
