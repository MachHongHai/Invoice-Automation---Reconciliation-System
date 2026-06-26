from app.utils import dedupe_invoice_items, extract_invoice_items, is_valid_invoice_item


def test_extract_invoice_items_rejects_ocr_noise_rows():
    text = """
1 | . | 855 | 0 | 0
2 | . | 710 | 0 | 0
3 | . | 710 | 0 | 0
4 | 0 | 0 | 0 | 0
5 | 0 | 0 | 0 | 0
6 | Ca chua (kg) | 34 | 24.000 | 816.000
7 | Khoai tay (kg) | 23 | 26.000 | 598.000
8 | Rau muong (kg) | 22 | 18.000 | 396.000
"""

    items = extract_invoice_items(text)

    assert [item["description"] for item in items] == ["Ca chua (kg)", "Khoai tay (kg)", "Rau muong (kg)"]
    assert not is_valid_invoice_item(".", 855, 0, 0)


def test_dedupe_invoice_items_removes_repeated_ocr_passes_and_overflow():
    items = [
        {"description": "Ca chua (kg)", "quantity": 34, "unit_price": 24000, "amount": 816000},
        {"description": "Khoai tay (kg)", "quantity": 23, "unit_price": 26000, "amount": 598000},
        {"description": "Rau muong (kg)", "quantity": 22, "unit_price": 18000, "amount": 396000},
        {"description": "Cai thia (kg)", "quantity": 7, "unit_price": 28000, "amount": 196000},
        {"description": "Ngheu song (kg)", "quantity": 18, "unit_price": 48000, "amount": 864000},
        {"description": "Ca chua (kg)", "quantity": 34, "unit_price": 24000, "amount": 816000},
    ]

    cleaned = dedupe_invoice_items(items, invoice_total=2024000)

    assert [item["description"] for item in cleaned] == [
        "Ca chua (kg)",
        "Khoai tay (kg)",
        "Rau muong (kg)",
        "Cai thia (kg)",
    ]
