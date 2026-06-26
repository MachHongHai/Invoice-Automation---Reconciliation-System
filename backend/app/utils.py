from __future__ import annotations

import csv
import io
import re
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


def decode_bytes(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def parse_csv_bytes(content: bytes) -> list[dict[str, str]]:
    text = decode_bytes(content)
    stream = io.StringIO(text)
    reader = csv.DictReader(stream)
    rows: list[dict[str, str]] = []
    for row in reader:
        normalized = {
            (key or "").strip().lower(): (value or "").strip()
            for key, value in row.items()
        }
        if any(normalized.values()):
            rows.append(normalized)
    return rows


def parse_tabular_file_bytes(file_name: str, content: bytes) -> list[dict[str, str]]:
    suffix = file_name.lower().rsplit(".", 1)[-1] if "." in file_name else "csv"
    if suffix in {"xlsx", "xls"}:
        import pandas as pd

        frame = pd.read_excel(io.BytesIO(content), dtype=str).fillna("")
    else:
        import pandas as pd

        text = decode_bytes(content)
        frame = pd.read_csv(io.StringIO(text), dtype=str).fillna("")

    rows: list[dict[str, str]] = []
    for record in frame.to_dict(orient="records"):
        normalized = {
            str(key).strip().lower(): str(value).strip()
            for key, value in record.items()
        }
        if any(normalized.values()):
            rows.append(normalized)
    return rows


def parse_amount(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    text = re.sub(r"(?i)\b(vnd|usd|eur)\b", "", text)
    text = text.replace(" ", "")

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        parts = text.split(",")
        text = "".join(parts) if all(len(part) == 3 for part in parts[1:]) else text.replace(",", ".")
    elif text.count(".") > 1:
        text = text.replace(".", "")

    text = re.sub(r"[^0-9.\-]", "", text)
    if not text:
        return None
    try:
        return float(Decimal(text))
    except (InvalidOperation, ValueError):
        return None


def parse_date(value: Any) -> str | None:
    if value is None or value == "":
        return None
    text = str(value).strip()
    formats = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y")
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def today_iso() -> str:
    return date.today().isoformat()


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _xml_text(root: ET.Element, paths: tuple[str, ...]) -> str | None:
    for path in paths:
        found = root.find(path)
        if found is not None and found.text and found.text.strip():
            return found.text.strip()
    return None


def parse_vietnam_einvoice_xml(content: bytes) -> dict[str, Any]:
    text = decode_bytes(content).strip()
    if not text:
        return {}
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return {}

    def pick(*paths: str) -> str | None:
        clean_paths = []
        for path in paths:
            clean_paths.append(path)
            clean_paths.append(f".//{{*}}{path.rsplit('/', 1)[-1]}")
        return _xml_text(root, tuple(clean_paths))

    title = pick(".//TTChung/THDon", "THDon") or ""
    template_code = pick(".//TTChung/KHMSHDon", "KHMSHDon")
    subtotal = parse_amount(pick(".//TToan/TgTCThue", "TgTCThue"))
    vat_amount = parse_amount(pick(".//TToan/TgTThue", "TgTThue"))
    total_amount = parse_amount(pick(".//TToan/TgTTTBSo", "TgTTTBSo"))
    vat_rate_text = pick(".//HHDVu/TSuat", "TSuat") or ""
    vat_rate = None
    if vat_rate_text and vat_rate_text not in {"KCT", "KKKNT", "KHAC"}:
        vat_rate = (parse_amount(vat_rate_text) or 0) / 100

    source_type = "vat_einvoice" if template_code == "1" or "GIA TRI GIA TANG" in normalize_text(title).upper() else "sales_einvoice"
    invoice_number = pick(".//TTChung/SHDon", "SHDon")
    invoice_series = pick(".//TTChung/KHHDon", "KHHDon")
    invoice_id = f"XML-{invoice_series}-{invoice_number}" if invoice_series and invoice_number else None

    return {
        "invoice_id": invoice_id,
        "invoice_number": invoice_number,
        "invoice_series": invoice_series,
        "invoice_template_code": template_code,
        "vendor_name": pick(".//NBan/Ten", "NBan/Ten"),
        "vendor_tax_code": pick(".//NBan/MST", "NBan/MST"),
        "vendor_bank_account": pick(".//NBan/STKNHang", "NBan/STKNHang"),
        "buyer_name": pick(".//NMua/Ten", "NMua/Ten"),
        "buyer_tax_code": pick(".//NMua/MST", "NMua/MST"),
        "invoice_date": parse_date(pick(".//TTChung/NLap", "NLap")),
        "subtotal": subtotal,
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,
        "total_amount": total_amount,
        "currency": (pick(".//TTChung/DVTTe", "DVTTe") or "VND").upper(),
        "source_type": source_type,
        "raw_text": text,
    }


def extract_invoice_fields(text: str, fallback_name: str = "") -> dict[str, Any]:
    haystack = f"{text}\n{fallback_name}"
    invoice_number = None
    invoice_match = re.search(r"\b(?:INV|HD|BILL|REC)[-\s_/]?\d{2,8}[-\s_/]?\d{2,8}\b", haystack, re.IGNORECASE)
    if invoice_match:
        invoice_number = re.sub(r"\s+", "-", invoice_match.group(0).upper())
    if not invoice_number:
        labelled = re.search(
            r"(?i)(?:so\s*hoa\s*don|so\s*hd|ma\s*phieu|ma\s*bien\s*nhan|receipt\s*no)\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-_/]{2,30})",
            haystack,
        )
        if labelled:
            invoice_number = labelled.group(1).upper()

    date_value = None
    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b", haystack)
    if date_match:
        date_value = parse_date(date_match.group(1))

    vendor_name = None
    vendor_match = re.search(
        r"(?im)^(?:nguoi\s*ban|nguoi\s*ban\s*hang|seller|vendor|moi\s*buon|nha\s*cung\s*cap)\s*[:\-]\s*(.+)$",
        haystack,
    )
    if vendor_match:
        vendor_name = vendor_match.group(1).strip()
    if not vendor_name:
        for line in haystack.splitlines()[:5]:
            candidate = line.strip(" :-")
            normalized = normalize_text(candidate)
            if candidate and "hoa don ban hang" not in normalized and "dia chi" not in normalized and "dt" != normalized:
                vendor_name = candidate
                break

    vendor_tax_code = None
    tax_match = re.search(
        r"(?i)(?:ma\s*so\s*thue|tax\s*code|mst)\s*[:\-]?\s*([0-9]{8,14})",
        haystack,
    )
    if tax_match:
        vendor_tax_code = tax_match.group(1)

    subtotal = None
    subtotal_match = re.search(
        r"(?i)(?:subtotal|cong\s*tien\s*hang|tien\s*hang)[^\d]{0,20}([0-9][0-9.,\s]*)",
        haystack,
    )
    if subtotal_match:
        subtotal = parse_amount(subtotal_match.group(1))

    total_amount = None
    total_patterns = (
        r"(?i)(?:total\s+amount|grand\s+total|amount\s+due|tong\s+tien\s+thanh\s+toan|tong\s+thanh\s+toan|tong\s+cong|thanh\s+toan|phai\s+tra)[^\d]{0,20}([0-9][0-9.,\s]*)",
        r"(?i)(?:thanh\s*tien)[^\d]{0,20}([0-9][0-9.,\s]*)\s*(?:vnd|dong)?",
        r"(?i)(?:total)[^\d]{0,20}([0-9][0-9.,\s]*)",
    )
    for pattern in total_patterns:
        match = re.search(pattern, haystack)
        if match:
            total_amount = parse_amount(match.group(1))
            if total_amount is not None:
                break

    vat_amount = None
    vat_match = re.search(r"(?i)(?:vat|tax)[^\d]{0,20}([0-9][0-9.,\s]*)", haystack)
    if vat_match:
        vat_amount = parse_amount(vat_match.group(1))

    currency = "VND"
    currency_match = re.search(r"(?i)\b(VND|USD|EUR)\b", haystack)
    if currency_match:
        currency = currency_match.group(1).upper()

    return {
        "invoice_number": invoice_number,
        "vendor_name": vendor_name,
        "vendor_tax_code": vendor_tax_code,
        "vendor_bank_account": vendor_bank_account,
        "invoice_date": date_value,
        "subtotal": subtotal,
        "total_amount": total_amount,
        "vat_amount": vat_amount,
        "currency": currency,
    }
    vendor_bank_account = None
    bank_match = re.search(
        r"(?i)(?:so\s*tai\s*khoan|stk|bank\s*account)\s*[:\-]?\s*([0-9]{6,24})",
        haystack,
    )
    if bank_match:
        vendor_bank_account = bank_match.group(1)
