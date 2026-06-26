# Data Dictionary

## vendor_master

- `vendor_id`: Internal vendor/moi buon ID.
- `vendor_name`: Legal or commonly used supplier name.
- `vendor_short_name`: Short name used in bank transfer descriptions.
- `tax_code`: Vendor tax code.
- `bank_account`: Vendor bank account used for payment control.
- `bank_name`: Vendor bank name.
- `bank_account_holder`: Uppercase unaccented account holder name for bank matching.
- `status`: `active` or `inactive`.

## invoice_register

- `invoice_id`: Internal invoice ID used to link XML, attachments, payment batch, and expected results.
- `invoice_number`: Legal invoice number or generated receipt number such as `REC-MMDD-XXXX`.
- `invoice_series`: E-invoice symbol/series when available.
- `invoice_template_code`: E-invoice form code when available. Sample uses `1` for VAT invoices and `2` for sales invoices.
- `document_type`: `pos_receipt`, `vendor_pdf_receipt`, `vat_einvoice`, or `sales_einvoice`.
- `vendor_id`, `vendor_tax_code`, `vendor_bank_account`: Vendor controls copied from invoice source.
- `subtotal`, `vat_rate`, `vat_amount`, `total_amount`: Financial values.
- `invoice_status`: Lifecycle status such as `validated`, `needs_review`, `rejected`, `approved_for_payment`.
- `source_type`: Source category, usually same as `document_type`.
- `attachment_file`: Related PDF/image attachment.
- `e_invoice_file`: Optional XML file for formal VAT/sales invoices.
- `expected_case`: Test scenario label.

## payment_batch

- `payment_id`: Payment approval or batch ID.
- `invoice_id`: Linked invoice.
- `approved_amount`: Amount approved for payment.
- `approval_status`: `draft`, `needs_review`, `approved`, `rejected`, `paid`, `reconciled`, or `exception`.
- `approved_by`, `approved_at`: Approval metadata.

## bank_statement

- `transaction_id`: Unique bank transaction ID.
- `transaction_date`, `value_date`: Bank transaction dates.
- `account_number`: Company bank account.
- `amount`: Positive transaction amount.
- `direction`: `inflow` or `outflow`.
- `counterparty_name`, `counterparty_account`: Vendor/customer counterparty details.
- `reference_code`: Invoice/payment reference when available.

## expected_reconciliation_results

- `invoice_id`: Linked invoice.
- `payment_id`: Linked payment if available.
- `expected_transaction_id`: Expected bank transaction if available.
- `expected_status`: Ground truth status.
- `expected_exception_type`: Ground truth exception type.
- `expected_amount_diff`: Expected amount difference.
- `expected_date_diff_days`: Expected date difference.
