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


def remove_vietnamese_accents(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("đ", "d").replace("Đ", "D")
    return text


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
    # Replace letter O/o with digit 0
    text = text.replace("O", "0").replace("o", "0")
    text = text.replace(" ", "")

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        parts = text.split(",")
        text = "".join(parts) if all(len(part) == 3 for part in parts[1:]) else text.replace(",", ".")
    elif "." in text:
        if text.count(".") > 1:
            text = text.replace(".", "")
        else:
            parts = text.split(".")
            # Single dot followed by exactly 3 digits is a thousands separator in Vietnamese context (especially VND)
            if len(parts[1]) == 3:
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


def extract_amount_by_keywords(lines: list[str], keywords: list[str]) -> float | None:
    # 1. Same line check
    for line in lines:
        for kw in keywords:
            unaccented_line = remove_vietnamese_accents(line)
            unaccented_kw = remove_vietnamese_accents(kw)

            match = re.search(rf"(?i){unaccented_kw}[^\d\n]{{0,20}}([0-9Oo][0-9Oo.,\s]*)", unaccented_line)
            if match:
                start, end = match.span(1)
                val_str = line[start:end]
                val = parse_amount(val_str)
                if val is not None:
                    return val

    # 2. Next line check
    for idx, line in enumerate(lines[:-1]):
        for kw in keywords:
            unaccented_line = remove_vietnamese_accents(line)
            unaccented_kw = remove_vietnamese_accents(kw)

            if re.search(rf"(?i)\b{unaccented_kw}\b", unaccented_line):
                next_line = lines[idx + 1].strip()
                clean_next = re.sub(r"(?i)\b(?:vnd|usd|eur|dong|d)\b", "", next_line).strip(" :-/.,|")
                numeric_check = clean_next.replace("O", "0").replace("o", "0")
                if re.match(r"^[0-9.,\s]+$", numeric_check):
                    val = parse_amount(clean_next)
                    if val is not None:
                        return val
    return None


def is_valid_invoice_item(
    description: Any,
    quantity: Any,
    unit_price: Any,
    amount: Any,
    *,
    invoice_total: Any = None,
) -> bool:
    cleaned_name = re.sub(r"\s+", " ", str(description or "").strip(" |,-.:;_"))
    normalized_name = normalize_text(cleaned_name)
    skip_keywords = {
        "stt",
        "ten hang",
        "don gia",
        "thanh tien",
        "so luong",
        "cong",
        "tong cong",
        "ngay",
        "khach hang",
        "nguoi ban",
        "dia chi",
        "hoa don",
        "mat hang ban",
    }
    if (
        not cleaned_name
        or len(cleaned_name) < 4
        or len(normalized_name) < 4
        or normalized_name in {"0", ".", "-", "_"}
        or any(keyword == normalized_name or keyword in normalized_name for keyword in skip_keywords)
        or not re.search(r"[A-Za-zÀ-ỹ]", cleaned_name)
        or not re.search(
            r"[aeiouyàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]",
            cleaned_name,
            re.IGNORECASE,
        )
    ):
        return False

    qty = parse_amount(quantity)
    price = parse_amount(unit_price)
    item_amount = parse_amount(amount)
    total = parse_amount(invoice_total)
    if qty is None or price is None or item_amount is None:
        return False
    if qty <= 0 or price <= 0 or item_amount <= 0:
        return False
    if qty != int(qty):
        return False
    if qty > 500 or price < 1_000 or item_amount < 1_000:
        return False
    if total is not None and total > 0 and item_amount > total * 1.02:
        return False
    expected_amount = qty * price
    if abs(expected_amount - item_amount) > max(5_000, item_amount * 0.08):
        return False
    return True


def dedupe_invoice_items(items: list[dict[str, Any]], invoice_total: Any = None) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int, int]] = set()
    total = parse_amount(invoice_total)
    running_amount = 0.0

    for item in items:
        description = item.get("description") or item.get("name")
        quantity = parse_amount(item.get("quantity"))
        unit_price = parse_amount(item.get("unit_price"))
        amount = parse_amount(item.get("amount"))
        if not is_valid_invoice_item(description, quantity, unit_price, amount, invoice_total=invoice_total):
            continue

        key = (
            normalize_text(str(description or "")),
            int(quantity or 0),
            int(round(unit_price or 0)),
            int(round(amount or 0)),
        )
        if key in seen:
            continue

        if total is not None and total > 0 and running_amount + float(amount or 0) > total + max(5_000, total * 0.02):
            continue

        seen.add(key)
        running_amount += float(amount or 0)
        normalized_item = dict(item)
        normalized_item["description"] = re.sub(r"\s+", " ", str(description or "").strip(" |,-.:;_"))
        normalized_item["quantity"] = quantity
        normalized_item["unit_price"] = unit_price
        normalized_item["amount"] = amount
        cleaned.append(normalized_item)

    return cleaned


def extract_invoice_items(text: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    lines = text.splitlines()
    skip_keywords = {
        "stt",
        "ten hang",
        "don gia",
        "thanh tien",
        "so luong",
        "cong",
        "tong cong",
        "ngay",
        "khach hang",
        "nguoi ban",
        "dia chi",
        "hoa don",
    }

    def add_item(name: str, qty_str: str, price_str: str, amt_str: str) -> None:
        cleaned_name = re.sub(r"\s+", " ", name.strip(" |,-.:;_"))
        normalized_name = normalize_text(cleaned_name)
        if (
            not cleaned_name
            or len(cleaned_name) < 4
            or len(normalized_name) < 4
            or any(keyword == normalized_name or keyword in normalized_name for keyword in skip_keywords)
            or not re.search(r"[A-Za-zÀ-ỹ]", cleaned_name)
            or not re.search(r"[aeiouyàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]", cleaned_name, re.IGNORECASE)
        ):
            return
        qty = parse_amount(qty_str)
        price = parse_amount(price_str)
        amount = parse_amount(amt_str)
        if qty is None or price is None:
            return
        if amount is None:
            amount = qty * price
        if not is_valid_invoice_item(cleaned_name, qty, price, amount):
            return
        items.append(
            {
                "description": cleaned_name,
                "quantity": qty,
                "unit_price": price,
                "amount": amount,
            }
        )

    for line in lines:
        line_clean = re.sub(r"\s+", " ", line.strip())
        if not line_clean:
            continue
        normalized = normalize_text(line_clean)
        if any(keyword == normalized or normalized.startswith(keyword) for keyword in skip_keywords):
            continue

        pipe_parts = [part.strip() for part in re.split(r"\s*[|]\s*", line_clean) if part.strip()]
        if len(pipe_parts) >= 5 and re.fullmatch(r"\d{1,2}", pipe_parts[0]):
            add_item(" ".join(pipe_parts[1:-3]), pipe_parts[-3], pipe_parts[-2], pipe_parts[-1])
            continue

        match = re.search(
            r"^\s*(\d{1,2})\s+(.{4,}?)\s+([0-9Oo]+(?:[,.][0-9Oo]+)?)\s+([0-9Oo][0-9Oo.,]{2,})\s+([0-9Oo][0-9Oo.,]{2,})\s*$",
            line_clean,
        )
        if match:
            _, name, qty_str, price_str, amt_str = match.groups()
            add_item(name, qty_str, price_str, amt_str)

    if not items:
        desc_candidates = []
        numbers = []
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            normalized = normalize_text(line_clean)
            if any(h in normalized for h in ["stt", "ten hang", "don gia", "thanh tien", "so luong", "ngay", "khach hang", "nguoi ban"]):
                continue
            if re.match(r"^[0-9Oo.,\s]+$", line_clean.replace("VND", "").replace("vnd", "").strip()):
                val = parse_amount(line_clean)
                if val is not None:
                    numbers.append(val)
            elif len(line_clean) > 3 and not any(kw in normalized for kw in ["dia chi", "mst", "dien thoai", "phone", "email", "fax"]):
                desc_candidates.append(line_clean)

        if len(desc_candidates) == 1 and len(numbers) >= 2:
            amt = numbers[-1]
            price = numbers[-2]
            qty = numbers[-3] if len(numbers) >= 3 else 1.0
            if qty * price != amt and price > 0:
                qty = round(amt / price, 2)
            if is_valid_invoice_item(desc_candidates[0], qty, price, amt):
                items.append({
                    "description": desc_candidates[0],
                    "quantity": qty,
                    "unit_price": price,
                    "amount": amt
                })

    return dedupe_invoice_items(items)


def extract_invoice_fields(text: str, fallback_name: str = "") -> dict[str, Any]:
    haystack = f"{text}\n{fallback_name}"
    invoice_number = None
    invoice_match = re.search(r"\b(?:INV|HD|BILL|REC)[-\s_/]?\d{2,8}[-\s_/]?\d{2,8}\b", haystack, re.IGNORECASE)
    if invoice_match:
        invoice_number = re.sub(r"\s+", "-", invoice_match.group(0).upper())
    if not invoice_number:
        labelled = re.search(
            r"(?i)(?:so\s*hoa\s*don|so\s*hd|ma\s*phieu|ma\s*bien\s*nhan|receipt\s*no|số|so)\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-_/]{2,30})",
            haystack,
        )
        if labelled:
            invoice_number = labelled.group(1).upper()

    date_value = None
    date_match = re.search(r"\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b", haystack)
    if date_match:
        date_value = parse_date(date_match.group(1))

    if not date_value:
        vn_date_match = re.search(
            r"(?i)(?:ngày|ngay)\s*(\d{1,2})\s*(?:tháng|thang)\s*(\d{1,2})\s*(?:năm|nam)\s*(\d{4})",
            haystack,
        )
        if vn_date_match:
            day, month, year = vn_date_match.groups()
            date_value = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # Identify tax codes only when the nearby label is tax-related. Phone numbers and bank accounts
    # often have the same length as Vietnamese tax codes on small paper receipts.
    all_tax_codes = []
    for match in re.finditer(r"\b([0-9]{10}(?:-[0-9]{3})?|[0-9]{13}|[0-9]{10})\b", haystack):
        prefix = haystack[max(0, match.start() - 40):match.start()]
        prefix_normalized = normalize_text(prefix)
        if any(label in prefix_normalized for label in ["mst", "ma so thue", "tax code"]):
            all_tax_codes.append(match.group(1))
    unique_tax_codes = []
    for tc in all_tax_codes:
        if tc not in unique_tax_codes:
            unique_tax_codes.append(tc)

    vendor_tax_code = None
    buyer_tax_code = None

    # Try to find vendor tax code using label
    vendor_tax_label = re.search(
        r"(?i)(?:mã\s*số\s*thuế\s*(?:người\s*bán|đơn\s*vị\s*bán|nhà\s*cung\s*cấp)|mst\s*(?:người\s*bán|đơn\s*vị\s*bán|nhà\s*cung\s*cấp|seller|vendor))\s*[:\-]?\s*([0-9]{10}(?:-[0-9]{3})?|[0-9]{13}|[0-9]{10})",
        haystack
    )
    if vendor_tax_label:
        vendor_tax_code = vendor_tax_label.group(1)

    # Try to find buyer tax code using label
    buyer_tax_label = re.search(
        r"(?i)(?:mã\s*số\s*thuế\s*(?:người\s*mua|khách\s*hàng|đơn\s*vị\s*mua)|mst\s*(?:người\s*mua|khách\s*hàng|buyer|customer))\s*[:\-]?\s*([0-9]{10}(?:-[0-9]{3})?|[0-9]{13}|[0-9]{10})",
        haystack
    )
    if buyer_tax_label:
        buyer_tax_code = buyer_tax_label.group(1)

    # Fallbacks for tax codes based on order of appearance
    if not vendor_tax_code and unique_tax_codes:
        vendor_tax_code = unique_tax_codes[0]
    if not buyer_tax_code and len(unique_tax_codes) > 1:
        if unique_tax_codes[0] == vendor_tax_code:
            buyer_tax_code = unique_tax_codes[1]
        else:
            buyer_tax_code = unique_tax_codes[0]

    vendor_name = None
    vendor_match = re.search(
        r"(?im)^(?:người\s*bán|nguoi\s*ban|người\s*bán\s*hàng|nguoi\s*ban\s*hang|seller|vendor|nhà\s*cung\s*cấp|nha\s*cung\s*cap)\s*[:\-]\s*(.+)$",
        haystack,
    )
    if vendor_match:
        vendor_name = vendor_match.group(1).strip()
    if not vendor_name:
        for line in haystack.splitlines()[:8]:
            candidate = line.strip(" :-")
            unaccented_candidate = remove_vietnamese_accents(candidate)

            # Remove title phrases using unaccented check
            title_match = re.search(
                r"(?i)\b(?:hoa\s*don\s*ban\s*hang|hoa\s*don\s*gtgt|hoa\s*don\s*gia\s*tri\s*gia\s*tang|hoa\s*don|phieu\s*thu|phieu\s*xuat\s*kho|lien\s*\d+|invoice|bill\s*of\s*sale)\b",
                unaccented_candidate
            )
            if title_match:
                start, end = title_match.span()
                candidate = (candidate[:start] + candidate[end:]).strip(" :-/.,")
                unaccented_candidate = remove_vietnamese_accents(candidate)

            # Split at address, phone, tax code metadata keywords
            meta_match = re.search(
                r"(?i)\b(?:dia\s*chis?|dt|dien\s*thoai|mst|ma\s*so\s*thue|mat\s*hang\s*ban|phone|email|fax)\b",
                unaccented_candidate
            )
            if meta_match:
                candidate = candidate[:meta_match.start()].strip(" :-/.,")

            normalized = normalize_text(candidate)
            if (
                candidate
                and len(candidate) > 3
                and "dia chi" not in normalized
                and "dien thoai" not in normalized
                and "phone" not in normalized
                and "email" not in normalized
                and "fax" not in normalized
                and "mst" not in normalized
                and "ma so thue" not in normalized
                and normalized != "dt"
            ):
                vendor_name = candidate
                break

    buyer_name = None
    buyer_match = re.search(
        r"(?im)(?:tên\s*khách\s*hàng|ten\s*khach\s*hang|người\s*mua|nguoi\s*mua|người\s*mua\s*hàng|nguoi\s*mua\s*hang|khách\s*hàng|khach\s*hang|buyer|customer)\s*[:\-]\s*(.+)$",
        haystack,
    )
    if buyer_match:
        buyer_name = buyer_match.group(1).strip()
        # Clean buyer_name of combined metadata/address
        unaccented_buyer = remove_vietnamese_accents(buyer_name)
        meta_match = re.search(
            r"(?i)\b(?:dia\s*chis?|dt|dien\s*thoai|mst|ma\s*so\s*thue|mat\s*hang\s*ban|phone|email|fax)\b",
            unaccented_buyer
        )
        if meta_match:
            buyer_name = buyer_name[:meta_match.start()].strip(" :-/.,")

    # Split text into lines for multi-line checks
    lines = text.splitlines()

    subtotal = extract_amount_by_keywords(
        lines,
        ["subtotal", "cộng tiền hàng", "cong tien hang", "tiền hàng", "tien hang", "cộng", "cong"]
    )

    total_amount = extract_amount_by_keywords(
        lines,
        [
            "total amount", "grand total", "amount due", "tổng cộng", "tong cong",
            "tổng tiền thanh toán", "tong tien thanh toan", "tổng thanh toán", "tong thanh toan",
            "thanh toán", "thanh toan", "thành tiền", "thanh tien", "phải trả", "phai tra", "total",
            "cộng", "cong"
        ]
    )

    vat_amount = extract_amount_by_keywords(
        lines,
        ["vat", "tax", "thuế gtgt", "thue gtgt", "tiền thuế", "tien thue"]
    )

    parsed_items = extract_invoice_items(text)
    items_total = sum(float(item.get("amount") or 0) for item in parsed_items)
    if items_total > 0:
        if subtotal is None:
            subtotal = items_total
        if total_amount is None:
            total_amount = items_total + (vat_amount or 0)

    currency = "VND"
    currency_match = re.search(r"(?i)\b(VND|USD|EUR)\b", haystack)
    if currency_match:
        currency = currency_match.group(1).upper()

    vendor_bank_account = None
    bank_match = re.search(
        r"(?i)(?:số\s*tài\s*khoản|so\s*tai\s*khoan|stk|bank\s*account)\s*[:\-]?\s*([0-9]{6,24})",
        haystack,
    )
    if bank_match:
        vendor_bank_account = bank_match.group(1)

    vendor_address = None
    address_match = re.search(
        r"(?i)(?:địa\s*chỉ|dia\s*chi)\s*[:\-]?\s*([^|\n]+)",
        haystack
    )
    if address_match:
        vendor_address = address_match.group(1).strip(" .:-/_,")

    vendor_phone = None
    phone_match = re.search(
        r"(?i)(?:đt|dt|điện\s*thoại|dien\s*thoai|sđt|sdt|phone|tel)\s*[:\-]?\s*([0-9\s.\-+]{8,20})",
        haystack
    )
    if phone_match:
        vendor_phone = phone_match.group(1).strip()

    return {
        "invoice_number": invoice_number,
        "vendor_name": vendor_name,
        "vendor_tax_code": vendor_tax_code,
        "vendor_bank_account": vendor_bank_account,
        "vendor_address": vendor_address,
        "vendor_phone": vendor_phone,
        "buyer_name": buyer_name,
        "buyer_tax_code": buyer_tax_code,
        "invoice_date": date_value,
        "subtotal": subtotal,
        "total_amount": total_amount,
        "vat_amount": vat_amount,
        "currency": currency,
    }
