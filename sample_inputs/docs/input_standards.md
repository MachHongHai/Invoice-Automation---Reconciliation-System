# Input Standards

FinRecon AI sample data follows a small F&B/restaurant workflow. Receipt images, simple PDF bills, and Excel registers are the primary operational inputs. Vietnamese e-invoice XML is supported as an optional clean source for formal suppliers.

## 1. Vendor master

Files: `vendor_master.csv`, `vendor_master.xlsx`

Columns:

```csv
vendor_id,vendor_name,vendor_short_name,tax_code,bank_account,bank_name,bank_account_holder,address,email,phone,category,status
```

## 2. Invoice register Excel/CSV

Files: `invoice_register.csv`, `invoice_register.xlsx`

This is the batch register used when the accountant already has a list of purchase receipts.

```csv
invoice_id,invoice_number,invoice_series,invoice_template_code,document_type,invoice_date,due_date,vendor_id,vendor_name,vendor_tax_code,vendor_bank_account,buyer_name,buyer_tax_code,subtotal,vat_rate,vat_amount,total_amount,currency,invoice_status,source_type,attachment_file,e_invoice_file,expected_case
```

## 3. E-invoice XML

Files: `raw/einvoice_xml/*.xml`

XML is optional and uses a Vietnam-style e-invoice envelope:

```text
HDon
  DLHDon
    TTChung: THDon, KHMSHDon, KHHDon, SHDon, NLap, DVTTe
    NDHDon
      NBan: Ten, MST, DChi, STKNHang, TNHang
      NMua: Ten, MST
      DSHHDVu/HHDVu: THHDVu, DVTinh, SLuong, DGia, ThTien, TSuat, TThue
      TToan: TgTCThue, TgTThue, TgTTTBSo, TgTTTBChu
  MCCQT
```

`KHMSHDon=1` is used for VAT invoices. `KHMSHDon=2` is used for sales invoices in this sample set.

## 4. Invoice attachments PDF/image

Files: `invoice_attachments/pdf/*.pdf`, `invoice_attachments/images/*.png`

Receipt images/PDFs are first-class inputs for the restaurant workflow. They are parsed with OCR/fallback extraction and can be quick-edited by the user.

## 5. Payment batch

Files: `payment_batch.csv`, `payment_batch.xlsx`

```csv
payment_id,invoice_id,vendor_id,scheduled_payment_date,approved_amount,currency,approval_status,approved_by,approved_at,payment_method,notes
```

## 6. Bank statement

Files: `bank_statement.csv`, `bank_statement.xlsx`

```csv
transaction_id,transaction_date,value_date,account_number,description,amount,direction,currency,balance_after,counterparty_name,counterparty_account,reference_code,expected_case
```

## 7. Expected reconciliation results

File: `expected_reconciliation_results.csv`

```csv
invoice_id,payment_id,expected_transaction_id,expected_status,expected_exception_type,expected_amount_diff,expected_date_diff_days,notes
```
