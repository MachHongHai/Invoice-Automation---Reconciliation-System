# FinRecon AI Sample Inputs

This folder contains synthetic sample inputs for the small F&B/restaurant workflow. The primary workflow is receipt-first: vendors/moi buon send POS receipts, simple delivery notes, PDFs, or phone photos. Vietnamese e-invoice XML files are kept as an optional clean source for formal suppliers such as beer, gas, packaging, supermarket ingredients, or utilities.

Thu muc nay chua du lieu mau cho nha hang nho/F&B. Luong chinh la phieu nhap hang, anh/PDF bien nhan, bang ke thanh toan va sao ke ngan hang. XML hoa don dien tu duoc giu nhu nguon phu khi nha cung cap co xuat hoa don VAT/hoa don ban hang dung chuan.

## Generate

```powershell
python sample_inputs/scripts/generate_all_inputs.py
```

Generated primary files:

- `raw/vendor_master.csv` and `.xlsx`
- `raw/invoice_register.csv` and `.xlsx`
- `raw/einvoice_xml/*.xml` for optional Vietnamese e-invoice VAT/sales invoice samples
- `raw/invoice_attachments/pdf/*.pdf`
- `raw/invoice_attachments/images/*.png`
- `raw/payment_batch.csv` and `.xlsx`
- `raw/bank_statement.csv` and `.xlsx`
- `raw/expected_reconciliation_results.csv`

## Source mix

- `pos_receipt`: market/vendor receipt image, intended for OCR fallback.
- `vendor_pdf_receipt`: simple PDF delivery note or retail bill.
- `vat_einvoice`: Vietnamese electronic VAT invoice XML using `HDon/DLHDon/TTChung/NBan/NMua/DSHHDVu/TToan`.
- `sales_einvoice`: Vietnamese electronic sales invoice XML using the same XML envelope with sales-invoice type code.

Validate only:

```powershell
python sample_inputs/scripts/validate_sample_inputs.py
```
