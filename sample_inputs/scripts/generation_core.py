from __future__ import annotations

import csv
import io
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from xml.sax.saxutils import escape
from typing import Any

import pandas as pd
import yaml
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


SAMPLE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = SAMPLE_ROOT / "config" / "generation_config.yaml"
RAW_DIR = SAMPLE_ROOT / "raw"
PROCESSED_DIR = SAMPLE_ROOT / "processed"
ATTACHMENT_DIR = RAW_DIR / "invoice_attachments"
PDF_DIR = ATTACHMENT_DIR / "pdf"
IMAGE_DIR = ATTACHMENT_DIR / "images"
EINVOICE_DIR = RAW_DIR / "einvoice_xml"


VENDOR_COLUMNS = [
    "vendor_id",
    "vendor_name",
    "vendor_short_name",
    "tax_code",
    "bank_account",
    "bank_name",
    "bank_account_holder",
    "address",
    "email",
    "phone",
    "category",
    "business_line",
    "status",
]

INVOICE_COLUMNS = [
    "invoice_id",
    "invoice_number",
    "invoice_series",
    "invoice_template_code",
    "document_type",
    "invoice_date",
    "due_date",
    "vendor_id",
    "vendor_name",
    "vendor_tax_code",
    "vendor_bank_account",
    "vendor_address",
    "vendor_phone",
    "business_line",
    "buyer_name",
    "buyer_tax_code",
    "subtotal",
    "vat_rate",
    "vat_amount",
    "total_amount",
    "currency",
    "invoice_status",
    "source_type",
    "attachment_file",
    "e_invoice_file",
    "expected_case",
]

PAYMENT_COLUMNS = [
    "payment_id",
    "invoice_id",
    "vendor_id",
    "scheduled_payment_date",
    "approved_amount",
    "currency",
    "approval_status",
    "approved_by",
    "approved_at",
    "payment_method",
    "notes",
]

BANK_COLUMNS = [
    "transaction_id",
    "transaction_date",
    "value_date",
    "account_number",
    "description",
    "amount",
    "direction",
    "currency",
    "balance_after",
    "counterparty_name",
    "counterparty_account",
    "reference_code",
    "expected_case",
]

EXPECTED_COLUMNS = [
    "invoice_id",
    "payment_id",
    "expected_transaction_id",
    "expected_status",
    "expected_exception_type",
    "expected_amount_diff",
    "expected_date_diff_days",
    "notes",
]


@dataclass
class GeneratedData:
    vendors: list[dict[str, Any]]
    invoices: list[dict[str, Any]]
    payments: list[dict[str, Any]]
    transactions: list[dict[str, Any]]
    expected_results: list[dict[str, Any]]


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def ensure_directories(clean: bool = False) -> None:
    if clean and RAW_DIR.exists():
        shutil.rmtree(RAW_DIR)
    if clean and PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)
    for directory in [RAW_DIR, PROCESSED_DIR, PDF_DIR, IMAGE_DIR, EINVOICE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_xlsx(path: Path, rows: list[dict[str, Any]], columns: list[str], sheet_name: str) -> None:
    frame = pd.DataFrame([{column: row.get(column, "") for column in columns} for row in rows])
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.book[sheet_name]
        worksheet.freeze_panes = "A2"
        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 42)


def generate_vendors() -> list[dict[str, Any]]:
    categories = [
        "thit_ca",
        "rau_cu",
        "gia_vi",
        "ruou_bia",
        "gas",
        "nuoc_da",
        "bao_bi",
        "dien_nuoc",
        "mat_bang",
        "tap_vu",
    ]
    names = [
        "Hộ Kinh Doanh Chị Lan Thịt Sạch",
        "Cửa Hàng Rau Củ Bác Hải",
        "Công Ty TNHH Hải Sản Cô Hương",
        "Trang Trại Gà Vịt Anh Nam",
        "Đại Lý Bia Nước Giải Khát Hưng Phát",
        "Công Ty Gas Petrolimex Chi Nhánh 3",
        "Cơ Sở Nước Đá Tuấn Ngọc",
        "Công Ty TNHH Bao Bì Gia Phát",
        "Siêu Thị Nguyên Liệu An Phú",
        "Công Ty Điện Lực Đông Đa",
    ]
    holders = [
        "NGUYỄN THỊ LAN",
        "TRẦN VĂN HẢI",
        "CÔNG TY TNHH HẢI SẢN CÔ HƯƠNG",
        "PHẠM VĂN NAM",
        "ĐẠI LÝ BIA HƯNG PHÁT",
        "CÔNG TY GAS PETROLIMEX CN3",
        "HKD NƯỚC ĐÁ TUẤN NGỌC",
        "CÔNG TY TNHH BAO BÌ GIA PHÁT",
        "CÔNG TY TNHH NGUYÊN LIỆU AN PHÚ",
        "CÔNG TY ĐIỆN LỰC ĐÔNG ĐA",
    ]
    business_lines = [
        "Thịt heo, bò, gà sơ chế",
        "Rau củ quả tươi Đà Lạt",
        "Hải sản tươi sống",
        "Gà vịt, trứng gia cầm",
        "Bia, nước giải khát",
        "Gas bếp công nghiệp",
        "Nước đá tinh khiết",
        "Bao bì, hộp giấy, ly nhựa",
        "Gia vị và nguyên liệu bếp",
        "Điện nước dịch vụ",
    ]
    vendors = []
    for index, name in enumerate(names, start=1):
        vendors.append(
            {
                "vendor_id": f"V{index:03d}",
                "vendor_name": name,
                "vendor_short_name": " ".join(name.split()[-3:]),
                "tax_code": f"03{index:08d}",
                "bank_account": f"{1234567890000 + index * 1111111}",
                "bank_name": ["Vietcombank", "ACB", "BIDV", "Techcombank", "VPBank"][index % 5],
                "bank_account_holder": holders[index - 1],
                "address": f"Quan {index}, TP. Ho Chi Minh",
                "email": f"contact{index:02d}@finrecon-demo.example",
                "phone": f"09000000{index:02d}",
                "category": categories[index - 1],
                "business_line": business_lines[index - 1],
                "status": "active",
            }
        )
    write_csv(RAW_DIR / "vendor_master.csv", vendors, VENDOR_COLUMNS)
    write_xlsx(RAW_DIR / "vendor_master.xlsx", vendors, VENDOR_COLUMNS, "Vendors")
    return vendors


def case_for_index(index: int) -> str:
    if index <= 30:
        return "validated_and_reconciled"
    if index <= 35:
        return "needs_review_before_payment"
    if index <= 38:
        return "rejected_before_payment"
    if index <= 42:
        return "approved_but_unpaid"
    if index <= 47:
        return "amount_mismatch_after_payment"
    return "unusual_amount"


def generate_invoice_register(vendors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    config = load_config()
    start_date = datetime.strptime(config["period"]["start_date"], "%Y-%m-%d").date()
    buyer = config["company"]
    vat_rate = float(config["vat_rate_default"])
    invoices = []
    for index in range(1, 51):
        case = case_for_index(index)
        vendor = vendors[(index - 1) % len(vendors)]
        invoice_id = f"INV-2026-{index:04d}"
        invoice_number = f"{index:08d}"
        invoice_series = "1C26TAA"
        if index == 37:
            invoice_number = "00000036"
        if index == 38:
            invoice_number = "00000036"
        invoice_date = start_date + timedelta(days=(index - 1) % 24)
        due_date = invoice_date + timedelta(days=7)
        subtotal = 350_000 + ((index % 9) * 420_000)
        if case == "unusual_amount":
            subtotal = 22_000_000 + (index * 100_000)
        document_type = "pos_receipt"
        invoice_template_code = "2"
        invoice_series = "2C26TAA"
        vat_for_invoice = 0.0
        attachment_file = f"{invoice_id}.png"
        e_invoice_file = ""
        if index <= 10:
            document_type = "vat_einvoice"
            invoice_template_code = "1"
            invoice_series = "1C26TAA"
            vat_for_invoice = vat_rate
            attachment_file = f"{invoice_id}.pdf"
            e_invoice_file = f"{invoice_id}.xml"
        elif index <= 15:
            document_type = "sales_einvoice"
            invoice_template_code = "2"
            invoice_series = "2C26TAA"
            vat_for_invoice = 0.0
            attachment_file = f"{invoice_id}.pdf"
            e_invoice_file = f"{invoice_id}.xml"
        elif index % 4 == 0:
            document_type = "vendor_pdf_receipt"
            attachment_file = f"{invoice_id}.pdf"
        vat_amount = round(subtotal * vat_for_invoice)
        total_amount = subtotal + vat_amount
        vendor_bank_account = vendor["bank_account"]
        vendor_name = vendor["vendor_name"]
        vendor_tax_code = vendor["tax_code"]
        vendor_id = vendor["vendor_id"]
        due_date_value = due_date.isoformat()
        invoice_status = "validated"
        if case == "needs_review_before_payment":
            invoice_status = "needs_review"
            due_date_value = "" if index in {31, 32} else due_date_value
            if index in {33, 34, 35}:
                vendor_bank_account = f"99999999{index:04d}"
        if case == "rejected_before_payment":
            invoice_status = "rejected"
            if index == 36:
                vendor_id = "V999"
                vendor_tax_code = "0399999999"
                vendor_name = "Cong ty Khong Ton Tai"
        if case in {"approved_but_unpaid", "amount_mismatch_after_payment", "unusual_amount"}:
            invoice_status = "approved_for_payment"
        row = {
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "invoice_series": invoice_series,
            "invoice_template_code": invoice_template_code,
            "document_type": document_type,
            "invoice_date": invoice_date.isoformat(),
            "due_date": due_date_value,
            "vendor_id": vendor_id,
            "vendor_name": vendor_name,
            "vendor_tax_code": vendor_tax_code,
            "vendor_bank_account": vendor_bank_account,
            "vendor_address": vendor.get("address", ""),
            "vendor_phone": vendor.get("phone", ""),
            "category": vendor.get("category", ""),
            "business_line": vendor.get("business_line", ""),
            "buyer_name": buyer["buyer_name"],
            "buyer_tax_code": buyer["buyer_tax_code"],
            "subtotal": subtotal,
            "vat_rate": vat_for_invoice,
            "vat_amount": vat_amount,
            "total_amount": total_amount,
            "currency": config["currency"],
            "invoice_status": invoice_status,
            "source_type": document_type,
            "attachment_file": attachment_file,
            "e_invoice_file": e_invoice_file,
            "expected_case": case,
        }
        line_items = build_receipt_items(row, target_amount=subtotal)
        row["line_items"] = line_items
        row["subtotal"] = sum(float(item["amount"]) for item in line_items)
        row["vat_amount"] = round(row["subtotal"] * vat_for_invoice)
        row["total_amount"] = row["subtotal"] + row["vat_amount"]
        invoices.append(row)
    write_csv(RAW_DIR / "invoice_register.csv", invoices, INVOICE_COLUMNS)
    write_xlsx(RAW_DIR / "invoice_register.xlsx", invoices, INVOICE_COLUMNS, "InvoiceRegister")
    return invoices


def money_words_stub(amount: float) -> str:
    return f"{int(amount):,} dong".replace(",", ".")


def build_vietnam_einvoice_xml(invoice: dict[str, Any]) -> str:
    is_vat = invoice["document_type"] == "vat_einvoice"
    invoice_title = "HOA DON GIA TRI GIA TANG" if is_vat else "HOA DON BAN HANG"
    tax_rate = f"{float(invoice['vat_rate']) * 100:.0f}%" if is_vat else "KCT"
    subtotal = float(invoice["subtotal"])
    vat_amount = float(invoice["vat_amount"] or 0)
    total = float(invoice["total_amount"])
    items = build_receipt_items(invoice, target_amount=subtotal, max_lines=5)
    item_xml = "\n".join(
        f"""        <HHDVu>
          <TChat>1</TChat>
          <STT>{index}</STT>
          <THHDVu>{escape(str(item["name"]))}</THHDVu>
          <DVTinh>{escape(str(item["unit"]))}</DVTinh>
          <SLuong>{float(item["quantity"]):g}</SLuong>
          <DGia>{float(item["unit_price"]):.0f}</DGia>
          <ThTien>{float(item["amount"]):.0f}</ThTien>
          <TSuat>{tax_rate}</TSuat>
          <TThue>{float(item["amount"]) * float(invoice["vat_rate"] or 0):.0f}</TThue>
        </HHDVu>"""
        for index, item in enumerate(items, start=1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<HDon>
  <DLHDon>
    <TTChung>
      <PBan>2.0.1</PBan>
      <THDon>{invoice_title}</THDon>
      <KHMSHDon>{escape(str(invoice["invoice_template_code"]))}</KHMSHDon>
      <KHHDon>{escape(str(invoice["invoice_series"]))}</KHHDon>
      <SHDon>{escape(str(invoice["invoice_number"]))}</SHDon>
      <NLap>{escape(str(invoice["invoice_date"]))}</NLap>
      <DVTTe>{escape(str(invoice["currency"]))}</DVTTe>
      <TGia>1</TGia>
      <HTTToan>TM/CK</HTTToan>
    </TTChung>
    <NDHDon>
      <NBan>
        <Ten>{escape(str(invoice["vendor_name"]))}</Ten>
        <MST>{escape(str(invoice["vendor_tax_code"] or ""))}</MST>
        <DChi>Cho dau moi / nha cung cap F&amp;B</DChi>
        <STKNHang>{escape(str(invoice["vendor_bank_account"] or ""))}</STKNHang>
        <TNHang>{escape(str(invoice.get("bank_name", "")))}</TNHang>
      </NBan>
      <NMua>
        <Ten>{escape(str(invoice["buyer_name"]))}</Ten>
        <MST>{escape(str(invoice["buyer_tax_code"]))}</MST>
      </NMua>
      <DSHHDVu>
{item_xml}
      </DSHHDVu>
      <TToan>
        <TgTCThue>{subtotal:.0f}</TgTCThue>
        <TgTThue>{vat_amount:.0f}</TgTThue>
        <TgTTTBSo>{total:.0f}</TgTTTBSo>
        <TgTTTBChu>{money_words_stub(total)}</TgTTTBChu>
      </TToan>
    </NDHDon>
  </DLHDon>
  <MCCQT>CQT{invoice["invoice_date"].replace("-", "")}{invoice["invoice_number"]}</MCCQT>
</HDon>
"""


def generate_einvoice_xml(invoices: list[dict[str, Any]]) -> list[Path]:
    paths: list[Path] = []
    for invoice in invoices:
        if not invoice.get("e_invoice_file"):
            continue
        path = EINVOICE_DIR / invoice["e_invoice_file"]
        path.write_text(build_vietnam_einvoice_xml(invoice), encoding="utf-8")
        paths.append(path)
    return paths



def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/timesbd.ttf" if bold else "C:/Windows/Fonts/times.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def money_vn(value: Any) -> str:
    return f"{float(value or 0):,.0f}".replace(",", ".")


FNB_ITEM_CATALOG: dict[str, list[tuple[str, str, float]]] = {
    "thit": [
        ("Thịt ba chỉ heo", "kg", 125_000),
        ("Sườn non heo", "kg", 145_000),
        ("Nạc vai heo", "kg", 118_000),
        ("Xương ống nấu nước dùng", "kg", 58_000),
        ("Mỡ heo thắng tóp", "kg", 42_000),
    ],
    "rau": [
        ("Rau muống", "kg", 18_000),
        ("Cải thìa", "kg", 28_000),
        ("Xà lách Đà Lạt", "kg", 38_000),
        ("Hành lá", "kg", 42_000),
        ("Cà chua", "kg", 24_000),
        ("Khoai tây", "kg", 26_000),
    ],
    "hai san": [
        ("Tôm thẻ loại 40 con", "kg", 185_000),
        ("Mực ống tươi", "kg", 210_000),
        ("Cá diêu hồng", "kg", 82_000),
        ("Nghêu sống", "kg", 48_000),
        ("Cá basa phi lê", "kg", 96_000),
    ],
    "ga": [
        ("Gà ta làm sạch", "kg", 112_000),
        ("Cánh gà", "kg", 88_000),
        ("Đùi gà góc tư", "kg", 72_000),
        ("Vịt làm sạch", "kg", 98_000),
        ("Trứng gà", "khay", 78_000),
    ],
    "bia": [
        ("Bia lon 333", "thùng", 285_000),
        ("Bia Saigon Special", "thùng", 360_000),
        ("Nước suối 500ml", "thùng", 78_000),
        ("Coca Cola lon", "thùng", 190_000),
        ("Nước ngọt Sprite", "thùng", 188_000),
    ],
    "gas": [
        ("Bình gas công nghiệp 45kg", "bình", 1_450_000),
        ("Bình gas 12kg", "bình", 430_000),
        ("Van gas thay thế", "cái", 120_000),
    ],
    "nuoc da": [
        ("Đá viên tinh khiết", "bao", 28_000),
        ("Đá cây", "cây", 36_000),
        ("Thùng xốp giữ lạnh", "cái", 55_000),
    ],
    "bao bi": [
        ("Hộp giấy 750ml", "lốc", 95_000),
        ("Túi nilon quai xách", "kg", 62_000),
        ("Ly nhựa 500ml", "lốc", 72_000),
        ("Ống hút giấy", "hộp", 45_000),
        ("Khăn giấy ăn", "thùng", 210_000),
    ],
    "default": [
        ("Nước mắm 5L", "can", 155_000),
        ("Dầu ăn 5L", "can", 185_000),
        ("Đường cát trắng", "kg", 25_000),
        ("Bột ngọt", "kg", 68_000),
        ("Gạo thơm", "kg", 22_000),
        ("Gia vị tổng hợp", "kg", 74_000),
    ],
}


def item_catalog_for_invoice(invoice: dict[str, Any]) -> list[tuple[str, str, float]]:
    vendor = normalize_for_catalog(invoice.get("vendor_name"))
    category = normalize_for_catalog(invoice.get("category") or invoice.get("expected_case"))
    lookup = f"{vendor} {category}"
    for key in ("hai san", "thit", "rau", "ga", "bia", "gas", "nuoc da", "bao bi"):
        if key in lookup:
            return FNB_ITEM_CATALOG[key]
    return FNB_ITEM_CATALOG["default"]


def normalize_for_catalog(value: Any) -> str:
    text = str(value or "").lower()
    replacements = {
        "á": "a", "à": "a", "ả": "a", "ã": "a", "ạ": "a",
        "ă": "a", "ắ": "a", "ằ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
        "â": "a", "ấ": "a", "ầ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
        "đ": "d",
        "é": "e", "è": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
        "ê": "e", "ế": "e", "ề": "e", "ể": "e", "ễ": "e", "ệ": "e",
        "í": "i", "ì": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
        "ó": "o", "ò": "o", "ỏ": "o", "õ": "o", "ọ": "o",
        "ô": "o", "ố": "o", "ồ": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
        "ơ": "o", "ớ": "o", "ờ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
        "ú": "u", "ù": "u", "ủ": "u", "ũ": "u", "ụ": "u",
        "ư": "u", "ứ": "u", "ừ": "u", "ử": "u", "ữ": "u", "ự": "u",
        "ý": "y", "ỳ": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def build_receipt_items(invoice: dict[str, Any], target_amount: float | None = None, max_lines: int = 6) -> list[dict[str, Any]]:
    existing_items = invoice.get("line_items")
    if isinstance(existing_items, list) and existing_items:
        return existing_items
    target = float(target_amount if target_amount is not None else invoice.get("total_amount") or invoice.get("subtotal") or 0)
    if target <= 0:
        return []
    catalog = item_catalog_for_invoice(invoice)
    invoice_index = int(str(invoice.get("invoice_id") or "0").split("-")[-1] or 0)
    line_count = min(max_lines, max(2, 2 + (invoice_index % 5)))
    line_count = min(line_count, len(catalog))
    start = invoice_index % len(catalog)
    selected = [catalog[(start + offset) % len(catalog)] for offset in range(line_count)]

    weights = [line_count - offset for offset in range(line_count)]
    items: list[dict[str, Any]] = []
    for offset, (name, unit, reference_price) in enumerate(selected):
        raw_amount = target * weights[offset] / sum(weights)
        quantity = max(1, round(raw_amount / reference_price))
        unit_price = reference_price
        amount = quantity * unit_price
        items.append(
            {
                "name": f"{name} ({unit})",
                "unit": unit,
                "quantity": quantity,
                "unit_price": unit_price,
                "amount": amount,
            }
        )
    return items


def draw_centered(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, font: ImageFont.ImageFont) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x1, y1, x2, y2 = box
    draw.text((x1 + (x2 - x1 - text_width) / 2, y1 + (y2 - y1 - text_height) / 2 - 1), text, fill=(0, 0, 0), font=font)


def fit_font(text: str, max_width: int, size: int, bold: bool = False, min_size: int = 10) -> ImageFont.ImageFont:
    for candidate_size in range(size, min_size - 1, -1):
        font = load_font(candidate_size, bold=bold)
        bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
    return load_font(min_size, bold=bold)


def draw_receipt_image(invoice: dict[str, Any], path: Path) -> None:
    width, height = 570, 501
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    title_font = load_font(17, bold=True)
    bold_font = load_font(16, bold=True)
    normal_font = load_font(16)
    small_font = load_font(14)
    tiny_font = load_font(13)

    vendor_name = str(invoice.get("vendor_name") or "TÊN CỬA HÀNG").upper()
    draw.text((18, 9), vendor_name, fill=(0, 0, 0), font=fit_font(vendor_name, 250, 17, bold=True, min_size=10))
    draw.text((294, 9), "HÓA ĐƠN BÁN HÀNG", fill=(0, 0, 0), font=title_font)
    vendor_address = str(invoice.get("vendor_address") or invoice.get("address") or "Chợ đầu mối / nhà cung cấp F&B")
    vendor_phone = str(invoice.get("vendor_phone") or invoice.get("phone") or "0900 000 000")
    draw.text((16, 36), f"Địa chỉ: {vendor_address[:24]}", fill=(0, 0, 0), font=small_font)
    draw.text((17, 57), f"ĐT: {vendor_phone}", fill=(0, 0, 0), font=small_font)
    business_line = str(invoice.get("business_line") or "Hàng hóa, nguyên liệu nhà hàng")
    business_text = f"Mặt hàng bán: {business_line}"
    draw.text((220, 47), business_text, fill=(0, 0, 0), font=fit_font(business_text, 330, 14, min_size=10))

    buyer_name = str(invoice.get("buyer_name") or "Nhà hàng FinRecon")
    draw.text((15, 103), f"Tên khách hàng: {buyer_name[:52]}", fill=(0, 0, 0), font=small_font)
    draw.text((15, 119), "Địa chỉ: 12 Nguyễn Huệ, Q.1, TP.HCM", fill=(0, 0, 0), font=small_font)

    x_cols = [14, 58, 214, 297, 418, 560]
    y_top = 137
    header_h = 38
    row_h = 19
    y_bottom = y_top + header_h + row_h * 11
    for x in x_cols:
        draw.line((x, y_top, x, y_bottom), fill=(0, 0, 0), width=1)
    for i in range(13):
        y = y_top if i == 0 else y_top + header_h + row_h * (i - 1)
        draw.line((x_cols[0], y, x_cols[-1], y), fill=(0, 0, 0), width=1)

    draw_centered(draw, (14, y_top, 58, y_top + header_h), "STT", bold_font)
    draw_centered(draw, (58, y_top, 214, y_top + header_h), "TÊN HÀNG", bold_font)
    draw_centered(draw, (214, y_top, 297, y_top + 19), "SỐ", bold_font)
    draw_centered(draw, (214, y_top + 17, 297, y_top + header_h), "LƯỢNG", bold_font)
    draw_centered(draw, (297, y_top, 418, y_top + header_h), "ĐƠN GIÁ", bold_font)
    draw_centered(draw, (418, y_top, 560, y_top + header_h), "THÀNH TIỀN", bold_font)

    rows = []
    items = build_receipt_items(invoice, target_amount=float(invoice.get("total_amount") or invoice.get("subtotal") or 0))
    for index, item in enumerate(items[:10], start=1):
        quantity = item["quantity"]
        quantity_text = f"{quantity:.1f}".rstrip("0").rstrip(".") if isinstance(quantity, float) else str(quantity)
        item_name = str(item["name"])
        if len(item_name) > 25:
            item_name = item_name[:24] + "."
        rows.append((str(index), item_name, quantity_text, money_vn(item["unit_price"]), money_vn(item["amount"])))
    for index in range(len(rows) + 1, 11):
        rows.append((str(index), "", "", "", ""))

    for index, row in enumerate(rows):
        y = y_top + header_h + row_h * index
        draw_centered(draw, (14, y, 58, y + row_h), row[0], small_font)
        draw.text((64, y + 2), row[1], fill=(0, 0, 0), font=tiny_font)
        draw_centered(draw, (214, y, 297, y + row_h), row[2], tiny_font)
        draw_centered(draw, (297, y, 418, y + row_h), row[3], tiny_font)
        draw_centered(draw, (418, y, 560, y + row_h), row[4], tiny_font)

    total_y = y_top + header_h + row_h * 10
    draw_centered(draw, (58, total_y, 214, total_y + row_h), "CỘNG", bold_font)
    draw_centered(draw, (418, total_y, 560, total_y + row_h), money_vn(invoice.get("total_amount")), tiny_font)

    draw.text((15, 408), f"Thành tiền: {money_vn(invoice.get('total_amount'))} VND", fill=(0, 0, 0), font=small_font)
    draw.line((95, 423, 550, 423), fill=(0, 0, 0), width=1)
    invoice_date = datetime.strptime(str(invoice["invoice_date"]), "%Y-%m-%d").date()
    draw.text((313, 429), f"Ngày {invoice_date.day:02d} tháng {invoice_date.month:02d} năm {invoice_date.year}", fill=(0, 0, 0), font=small_font)
    draw.text((28, 465), "KHÁCH HÀNG", fill=(0, 0, 0), font=normal_font)
    draw.text((294, 465), "NGƯỜI BÁN HÀNG", fill=(0, 0, 0), font=normal_font)
    buffer = io.BytesIO()
    image_format = "PDF" if path.suffix.lower() == ".pdf" else "PNG"
    img.save(buffer, format=image_format)
    path.write_bytes(buffer.getvalue())
    img.close()


def generate_invoice_attachments(invoices: list[dict[str, Any]]) -> list[Path]:
    paths = []
    for invoice in invoices:
        filename = invoice["attachment_file"]
        if filename.endswith(".png"):
            path = IMAGE_DIR / filename
            draw_receipt_image(invoice, path)
        else:
            path = PDF_DIR / filename
            draw_receipt_image(invoice, path)
            paths.append(path)
            continue
            doc = canvas.Canvas(str(path), pagesize=A4)
            width, height = A4

            # Professional border
            doc.setStrokeColorRGB(0.1, 0.3, 0.5)
            doc.setLineWidth(1.5)
            doc.rect(20, 20, width - 40, height - 40)

            doc.setFont("Helvetica-Bold", 18)
            doc.setFillColorRGB(0.1, 0.3, 0.5)
            doc.drawCentredString(width / 2, height - 60, "HOA DON GIA TRI GIA TANG")
            doc.setFont("Helvetica", 9)
            doc.drawCentredString(width / 2, height - 75, "(HOA DON DIEN TU / ELECTRONIC INVOICE)")

            # Seller info
            doc.setFont("Helvetica-Bold", 10)
            doc.drawString(40, height - 110, "NHA CUNG CAP (SELLER):")
            doc.setFont("Helvetica", 10)
            doc.drawString(40, height - 125, f"Nha cung cap: {invoice['vendor_name']}")
            doc.drawString(40, height - 140, f"Ma so thue (MST): {invoice['vendor_tax_code'] or 'N/A'}")
            doc.drawString(40, height - 155, f"So tai khoan: {invoice['vendor_bank_account'] or 'N/A'}")

            # Buyer info
            doc.setFont("Helvetica-Bold", 10)
            doc.drawString(40, height - 185, "DON VI MUA HANG (BUYER):")
            doc.setFont("Helvetica", 10)
            doc.drawString(40, height - 200, f"Ten don vi: {invoice['buyer_name']}")
            doc.drawString(40, height - 215, f"Ma so thue (MST): {invoice['buyer_tax_code']}")

            # Invoice Info
            doc.drawString(380, height - 110, f"Ky hieu: {invoice.get('invoice_series', 'N/A')}")
            doc.drawString(380, height - 125, f"Mau so: {invoice.get('invoice_template_code', 'N/A')}")
            doc.drawString(380, height - 140, f"Ma phieu: {invoice.get('invoice_number', 'N/A')}")
            doc.drawString(380, height - 155, f"Ngay lap: {invoice['invoice_date']}")

            doc.setStrokeColorRGB(0.7, 0.7, 0.7)
            doc.setLineWidth(0.5)
            doc.line(40, height - 230, width - 40, height - 230)

            # Items table
            doc.setFont("Helvetica-Bold", 10)
            doc.drawString(40, height - 250, "STT")
            doc.drawString(80, height - 250, "Ten hang hoa (Description)")
            doc.drawString(300, height - 250, "SL")
            doc.drawString(350, height - 250, "Don gia")
            doc.drawString(430, height - 250, "Thanh tien")
            doc.line(40, height - 255, width - 40, height - 255)

            subtotal = invoice["subtotal"]
            vat_rate = invoice["vat_rate"]
            vat_amount = invoice["vat_amount"]
            total = invoice["total_amount"]

            doc.setFont("Helvetica", 10)
            doc.drawString(40, height - 275, "1")
            doc.drawString(80, height - 275, "Thuc pham gia vi va nguyen lieu F&B")
            doc.drawString(300, height - 275, "1")
            doc.drawString(350, height - 275, f"{subtotal:,.0f}")
            doc.drawString(430, height - 275, f"{subtotal:,.0f}")

            doc.line(40, height - 350, width - 40, height - 350)

            # Totals
            doc.drawString(300, height - 370, "Cong tien hang (Subtotal):")
            doc.drawRightString(width - 40, height - 370, f"{subtotal:,.0f} VND")

            doc.drawString(300, height - 385, "Thue suat VAT (Tax %):")
            doc.drawRightString(width - 40, height - 385, f"{vat_rate * 100:.0f}%")

            doc.drawString(300, height - 400, "Tien thue VAT (Tax amount):")
            doc.drawRightString(width - 40, height - 400, f"{vat_amount:,.0f} VND")

            doc.setFont("Helvetica-Bold", 11)
            doc.drawString(300, height - 420, "TONG CONG THANH TOAN:")
            doc.drawRightString(width - 40, height - 420, f"{total:,.0f} VND")

            doc.line(40, height - 430, width - 40, height - 430)

            doc.setFont("Helvetica-Bold", 9)
            doc.drawString(100, height - 460, "NGUOI MUA HANG")
            doc.drawCentredString(width - 150, height - 460, "NGUOI BAN HANG")
            doc.setFont("Helvetica", 8)
            doc.drawString(80, height - 475, "(Ky, ghi ro ho ten)")
            doc.drawCentredString(width - 150, height - 475, "(Ky so dien tu, ngay ky)")

            doc.save()
        paths.append(path)
    return paths


def generate_payment_batch(invoices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payments = []
    payable_cases = {"validated_and_reconciled", "approved_but_unpaid", "amount_mismatch_after_payment", "unusual_amount"}
    for invoice in invoices:
        if invoice["expected_case"] not in payable_cases:
            continue
        payment = {
            "payment_id": invoice["invoice_id"].replace("INV", "PAY"),
            "invoice_id": invoice["invoice_id"],
            "vendor_id": invoice["vendor_id"],
            "scheduled_payment_date": invoice["due_date"] or invoice["invoice_date"],
            "approved_amount": invoice["total_amount"],
            "currency": invoice["currency"],
            "approval_status": "approved",
            "approved_by": "accountant_01",
            "approved_at": f"{invoice['invoice_date']} 09:30:00",
            "payment_method": "bank_transfer",
            "notes": "Ready for payment",
        }
        payments.append(payment)
    write_csv(RAW_DIR / "payment_batch.csv", payments, PAYMENT_COLUMNS)
    write_xlsx(RAW_DIR / "payment_batch.xlsx", payments, PAYMENT_COLUMNS, "PaymentBatch")
    return payments


def generate_bank_statement(invoices: list[dict[str, Any]], payments: list[dict[str, Any]], vendors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    config = load_config()
    account = config["company"]["buyer_bank_account"]
    invoice_by_id = {invoice["invoice_id"]: invoice for invoice in invoices}
    txns = []
    balance = 500_000_000
    transaction_index = 1
    for payment in payments:
        invoice = invoice_by_id[payment["invoice_id"]]
        case = invoice["expected_case"]
        if case == "approved_but_unpaid":
            continue
        txn_amount = float(payment["approved_amount"])
        if case == "amount_mismatch_after_payment":
            txn_amount -= 200_000
        scheduled = datetime.strptime(payment["scheduled_payment_date"], "%Y-%m-%d").date()
        txn_date = scheduled + timedelta(days=1 if case == "amount_mismatch_after_payment" else 0)
        balance -= txn_amount
        txns.append(
            {
                "transaction_id": f"TXN{transaction_index:04d}",
                "transaction_date": txn_date.isoformat(),
                "value_date": txn_date.isoformat(),
                "account_number": account,
                "description": f"ck tien {invoice['vendor_name'].lower().replace('chi lan moi thit', 'thit chi lan').replace('bac hai rau cu', 'rau bac hai')}",
                "amount": int(txn_amount),
                "direction": "outflow",
                "currency": invoice["currency"],
                "balance_after": int(balance),
                "counterparty_name": invoice["vendor_name"],
                "counterparty_account": invoice["vendor_bank_account"],
                "reference_code": invoice["invoice_id"],
                "expected_case": case,
            }
        )
        transaction_index += 1
    for extra in range(1, 4):
        balance -= 1_500_000 + extra * 100_000
        txns.append(
            {
                "transaction_id": f"TXN{transaction_index:04d}",
                "transaction_date": f"2026-06-{20 + extra:02d}",
                "value_date": f"2026-06-{20 + extra:02d}",
                "account_number": account,
                "description": f"Chi phi khong co payment {extra}",
                "amount": 1_500_000 + extra * 100_000,
                "direction": "outflow",
                "currency": "VND",
                "balance_after": int(balance),
                "counterparty_name": "Unknown Payee",
                "counterparty_account": f"88880000{extra}",
                "reference_code": f"UNMATCHED-{extra}",
                "expected_case": "unmatched_bank_transaction",
            }
        )
        transaction_index += 1
    while len(txns) < 65:
        balance += 2_000_000
        txns.append(
            {
                "transaction_id": f"TXN{transaction_index:04d}",
                "transaction_date": "2026-06-28",
                "value_date": "2026-06-28",
                "account_number": account,
                "description": "Customer receipt not relevant to AP reconciliation",
                "amount": 2_000_000,
                "direction": "inflow",
                "currency": "VND",
                "balance_after": int(balance),
                "counterparty_name": "Customer",
                "counterparty_account": f"77770000{transaction_index}",
                "reference_code": f"INFLOW-{transaction_index}",
                "expected_case": "ignored_inflow",
            }
        )
        transaction_index += 1
    write_csv(RAW_DIR / "bank_statement.csv", txns, BANK_COLUMNS)
    write_xlsx(RAW_DIR / "bank_statement.xlsx", txns, BANK_COLUMNS, "BankStatement")
    return txns


def generate_expected_reconciliation_results(invoices: list[dict[str, Any]], payments: list[dict[str, Any]], transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payment_by_invoice = {payment["invoice_id"]: payment for payment in payments}
    transaction_by_ref = {txn["reference_code"]: txn for txn in transactions if txn["direction"] == "outflow"}
    rows = []
    for invoice in invoices:
        payment = payment_by_invoice.get(invoice["invoice_id"])
        txn = transaction_by_ref.get(invoice["invoice_id"])
        case = invoice["expected_case"]
        status = case
        exception = ""
        amount_diff = ""
        date_diff = ""
        if case == "validated_and_reconciled":
            status = "reconciled"
            amount_diff = 0
            date_diff = 0
        elif case == "approved_but_unpaid":
            status = "unmatched_approved_invoice"
            exception = "unmatched_approved_invoice"
        elif case == "amount_mismatch_after_payment":
            status = "amount_mismatch"
            exception = "amount_mismatch"
            amount_diff = 200000
            date_diff = 1
        elif case == "needs_review_before_payment":
            status = "needs_review"
            exception = "vendor_bank_mismatch" if invoice["vendor_bank_account"].startswith("999") else "missing_required_field"
        elif case == "rejected_before_payment":
            status = "rejected"
            exception = "duplicate_invoice" if invoice["invoice_number"] == "00000036" else "vendor_not_found"
        elif case == "unusual_amount":
            status = "unusual_amount"
            exception = "unusual_amount"
        rows.append(
            {
                "invoice_id": invoice["invoice_id"],
                "payment_id": payment["payment_id"] if payment else "",
                "expected_transaction_id": txn["transaction_id"] if txn else "",
                "expected_status": status,
                "expected_exception_type": exception,
                "expected_amount_diff": amount_diff,
                "expected_date_diff_days": date_diff,
                "notes": f"Expected case: {case}",
            }
        )
    write_csv(RAW_DIR / "expected_reconciliation_results.csv", rows, EXPECTED_COLUMNS)
    return rows


def write_processed_samples(invoices: list[dict[str, Any]], payments: list[dict[str, Any]], expected: list[dict[str, Any]]) -> None:
    write_csv(PROCESSED_DIR / "normalized_invoices_sample.csv", invoices, INVOICE_COLUMNS)
    write_csv(
        PROCESSED_DIR / "invoice_validation_results_sample.csv",
        [
            {
                "invoice_id": invoice["invoice_id"],
                "validation_status": "valid" if invoice["expected_case"] in {"validated_and_reconciled", "approved_but_unpaid", "amount_mismatch_after_payment"} else invoice["invoice_status"],
                "expected_case": invoice["expected_case"],
            }
            for invoice in invoices
        ],
        ["invoice_id", "validation_status", "expected_case"],
    )
    write_csv(PROCESSED_DIR / "payment_approval_results_sample.csv", payments, PAYMENT_COLUMNS)
    write_csv(PROCESSED_DIR / "reconciliation_results_sample.csv", expected, EXPECTED_COLUMNS)


def validate_sample_inputs() -> dict[str, Any]:
    vendors = pd.read_csv(RAW_DIR / "vendor_master.csv", dtype=str).fillna("")
    invoices = pd.read_csv(RAW_DIR / "invoice_register.csv", dtype=str).fillna("")
    payments = pd.read_csv(RAW_DIR / "payment_batch.csv", dtype=str).fillna("")
    transactions = pd.read_csv(RAW_DIR / "bank_statement.csv", dtype=str).fillna("")
    expected = pd.read_csv(RAW_DIR / "expected_reconciliation_results.csv", dtype=str).fillna("")

    vendor_ids = set(vendors["vendor_id"])
    invoice_ids = set(invoices["invoice_id"])
    payment_ids = set(payments["payment_id"])
    transaction_ids = set(transactions["transaction_id"])
    errors = []
    for _, invoice in invoices.iterrows():
        if invoice["vendor_id"] not in vendor_ids and invoice["expected_case"] != "rejected_before_payment":
            errors.append(f"Invoice {invoice['invoice_id']} references missing vendor {invoice['vendor_id']}")
    for _, payment in payments.iterrows():
        if payment["invoice_id"] not in invoice_ids:
            errors.append(f"Payment {payment['payment_id']} references missing invoice")
    for _, row in expected.iterrows():
        if row["invoice_id"] not in invoice_ids:
            errors.append(f"Expected row references missing invoice {row['invoice_id']}")
        if row["payment_id"] and row["payment_id"] not in payment_ids:
            errors.append(f"Expected row references missing payment {row['payment_id']}")
        if row["expected_transaction_id"] and row["expected_transaction_id"] not in transaction_ids:
            errors.append(f"Expected row references missing transaction {row['expected_transaction_id']}")
    pd.read_excel(RAW_DIR / "vendor_master.xlsx", dtype=str)
    pd.read_excel(RAW_DIR / "invoice_register.xlsx", dtype=str)
    pd.read_excel(RAW_DIR / "payment_batch.xlsx", dtype=str)
    pd.read_excel(RAW_DIR / "bank_statement.xlsx", dtype=str)
    for xml_file in EINVOICE_DIR.glob("*.xml"):
        root = ET.parse(xml_file).getroot()
        if root.find(".//TTChung") is None or root.find(".//TToan") is None:
            errors.append(f"E-invoice XML is missing TTChung/TToan: {xml_file.name}")
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "vendors": len(vendors),
        "invoices": len(invoices),
        "payments": len(payments),
        "transactions": len(transactions),
        "expected": len(expected),
    }


def generate_all_inputs(clean: bool = True) -> GeneratedData:
    ensure_directories(clean=clean)
    vendors = generate_vendors()
    invoices = generate_invoice_register(vendors)
    generate_einvoice_xml(invoices)
    generate_invoice_attachments(invoices)
    payments = generate_payment_batch(invoices)
    transactions = generate_bank_statement(invoices, payments, vendors)
    expected = generate_expected_reconciliation_results(invoices, payments, transactions)
    write_processed_samples(invoices, payments, expected)
    validate_sample_inputs()
    return GeneratedData(vendors, invoices, payments, transactions, expected)


def print_summary(data: GeneratedData) -> None:
    print(f"Generated vendors: {len(data.vendors)}")
    print(f"Generated e-invoice XML files: {len(list(EINVOICE_DIR.glob('*.xml')))}")
    print(f"Generated invoice PDF attachments: {len(list(PDF_DIR.glob('*.pdf')))}")
    print(f"Generated invoice PNG attachments (handwritten receipts): {len(list(IMAGE_DIR.glob('*.png')))}")
    print(f"Generated payment batch rows: {len(data.payments)}")
    print(f"Generated bank transactions: {len(data.transactions)}")
    print(f"Generated expected reconciliation rows: {len(data.expected_results)}")
    print(f"Output folder: {RAW_DIR}")
