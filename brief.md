# FinRecon AI – Invoice Automation & Bank Reconciliation Platform

## 1. Mục tiêu dự án

Xây dựng một hệ thống **Invoice Automation & Bank Reconciliation** dùng để tự động hóa quy trình xử lý hóa đơn và đối soát giao dịch ngân hàng.

Dự án này được thiết kế như một **flagship project** cho CV ngành:

- Data Analyst
- Data Scientist
- Analytics Engineer
- AI Automation Engineer
- Data Automation
- Business/Data Product Intern

Ý tưởng chính:

```text
Upload invoice PDF/image + bank statement Excel/CSV
        ↓
OCR đọc hóa đơn
        ↓
Extract thông tin quan trọng
        ↓
Validate dữ liệu
        ↓
Match với giao dịch ngân hàng
        ↓
Flag lỗi đối soát
        ↓
Dashboard + AI explanation/report
```

---

## 2. Vì sao dự án này có giá trị cao?

Đây không phải là một project EDA/dashboard đơn giản. Dự án này mô phỏng một bài toán thực tế trong doanh nghiệp:

- Kế toán nhận nhiều hóa đơn PDF/ảnh.
- Nhân viên phải nhập thủ công thông tin hóa đơn.
- Sau đó phải đối chiếu hóa đơn với sao kê ngân hàng.
- Các lỗi thường gặp:
  - Hóa đơn trùng
  - Thanh toán thiếu/thừa
  - Không tìm thấy giao dịch ngân hàng
  - Có giao dịch ngân hàng nhưng thiếu hóa đơn
  - Sai nhà cung cấp
  - Sai VAT/tổng tiền
  - OCR đọc sai dữ liệu

Dự án thể hiện được nhiều kỹ năng quan trọng:

- Python
- SQL
- PostgreSQL
- FastAPI
- React/Next.js
- OCR
- Data validation
- Fuzzy matching
- Reconciliation logic
- Dashboard
- AI explanation
- Docker
- Background jobs
- Business analytics

---

## 3. Tên project đề xuất

Tên chính:

```text
FinRecon AI
```

Tên đầy đủ:

```text
FinRecon AI – Invoice Automation & Bank Reconciliation Platform
```

Một số tên khác:

```text
InvoiceFlow AI
AutoRecon
LedgerMatch AI
FinanceOps Automation Platform
AI Invoice Reconciliation Platform
```

---

## 4. Input của dự án

Người làm project không cần dữ liệu tài chính thật. Dữ liệu thật thường nhạy cảm, chứa thông tin như mã số thuế, địa chỉ, tài khoản ngân hàng, chữ ký, giao dịch thanh toán.

Cách làm chuyên nghiệp hơn là tự tạo **synthetic data** mô phỏng quy trình tài chính doanh nghiệp.

Input gồm 3 nhóm chính:

```text
1. Invoice files: PDF / ảnh hóa đơn
2. Bank statement: file Excel/CSV giao dịch ngân hàng
3. Vendor master: file Excel/CSV danh sách nhà cung cấp
```

---

## 5. Dataset tự tạo

### 5.1. Cấu trúc thư mục dữ liệu

```text
data/
├── raw/
│   ├── invoices/
│   │   ├── INV-2026-001.pdf
│   │   ├── INV-2026-002.pdf
│   │   ├── INV-2026-003.png
│   │   └── ...
│   │
│   ├── bank_statement.csv
│   ├── vendor_master.csv
│   └── expected_matches.csv
│
├── processed/
│   ├── extracted_invoices.csv
│   ├── validation_results.csv
│   └── reconciliation_results.csv
```

### 5.2. Quy mô dữ liệu đề xuất

Bản MVP:

```text
10 hóa đơn PDF
1 file bank_statement.csv khoảng 15 giao dịch
1 file vendor_master.csv khoảng 5 vendor
```

Bản portfolio chuyên nghiệp:

```text
50 invoice PDF/image
65 bank transactions
10 vendors
1 expected_matches.csv
10–15 reconciliation exceptions
```

---

## 6. Công ty giả lập

Sử dụng công ty giả để tạo dữ liệu:

```text
Tên công ty: Demo Retail Co., Ltd.
Ngành: Bán lẻ thiết bị văn phòng
Thời gian dữ liệu: 01/06/2026 - 30/06/2026
Số vendor: 10
Số hóa đơn: 50
Số giao dịch ngân hàng: 65
```

---

## 7. Vendor master

File `vendor_master.csv` chứa danh sách nhà cung cấp.

Ví dụ:

```csv
vendor_id,vendor_name,tax_code,bank_account,address
V001,Công ty TNHH Minh Anh,0312345678,123456789,Bình Thạnh TP.HCM
V002,Công ty CP Sao Việt,0311112222,987654321,Quận 1 TP.HCM
V003,Công ty TNHH Hòa Bình,0301234567,555666777,Quận 3 TP.HCM
V004,Công ty Dịch vụ Ánh Dương,0318889999,111222333,Thủ Đức TP.HCM
V005,Công ty Phú Gia,0315556666,444555666,Tân Bình TP.HCM
V006,Công ty Việt Cloud,0317778888,888999000,Quận 7 TP.HCM
```

Vendor master giúp hệ thống:

- Kiểm tra vendor có tồn tại không.
- So khớp tên vendor khi OCR đọc sai.
- Kiểm tra tài khoản ngân hàng.
- Chuẩn hóa tên nhà cung cấp.

Ví dụ OCR đọc:

```text
Cong ty TNHH Minh Anh
```

Vendor master lưu:

```text
Công ty TNHH Minh Anh
```

Hệ thống dùng fuzzy matching để hiểu đây là cùng một vendor.

---

## 8. Invoice PDF/image

Mỗi hóa đơn nên có các field:

```text
Tên hóa đơn: HÓA ĐƠN GIÁ TRỊ GIA TĂNG
Số hóa đơn: INV-2026-001
Ngày lập: 05/06/2026

Người bán:
Công ty TNHH Minh Anh
Mã số thuế: 0312345678
Địa chỉ: Quận Bình Thạnh, TP.HCM
Số tài khoản: 123456789

Người mua:
Công ty TNHH Demo Retail
Mã số thuế: 0309999999

Hàng hóa:
1. Dịch vụ phần mềm POS - 1 gói - 5,000,000
2. Phí bảo trì hệ thống - 1 gói - 500,000

Cộng tiền hàng: 5,500,000
VAT 10%: 550,000
Tổng thanh toán: 6,050,000 VND
```

Sau OCR và extraction, output mong muốn:

```json
{
  "invoice_number": "INV-2026-001",
  "vendor_name": "Công ty TNHH Minh Anh",
  "vendor_tax_code": "0312345678",
  "invoice_date": "2026-06-05",
  "subtotal": 5500000,
  "vat_amount": 550000,
  "total_amount": 6050000,
  "currency": "VND"
}
```

---

## 9. Bank statement

File `bank_statement.csv` mô phỏng sao kê ngân hàng.

Ví dụ:

```csv
transaction_id,transaction_date,description,amount,direction,bank_account
TXN001,2026-06-07,Thanh toan hoa don INV-2026-001 Cong ty Minh Anh,6050000,outflow,123456789
TXN002,2026-06-09,CK HD INV-2026-002 CTY SAO VIET,3300000,outflow,123456789
TXN003,2026-06-10,Thanh toan NCC Hoa Binh,11000000,outflow,123456789
TXN004,2026-06-12,Phi dich vu ngan hang,22000,outflow,123456789
TXN005,2026-06-13,Thanh toan hoa don INV-2026-006,4950000,outflow,123456789
```

Hệ thống sẽ match hóa đơn với giao dịch dựa trên:

```text
- Số tiền
- Ngày giao dịch
- Tên vendor
- Nội dung chuyển khoản
- Số hóa đơn
- Mã số thuế hoặc tài khoản ngân hàng nếu có
```

---

## 10. Expected matches

File `expected_matches.csv` dùng làm ground truth để kiểm tra hệ thống match đúng hay không.

Ví dụ:

```csv
invoice_number,expected_transaction_id,expected_status,expected_exception
INV-2026-001,TXN001,matched,
INV-2026-002,TXN002,matched,
INV-2026-003,TXN003,amount_mismatch,amount_mismatch
INV-2026-004,,unmatched_invoice,missing_bank_transaction
INV-2026-005,,duplicate_invoice,duplicate_invoice_number
```

---

## 11. Case lỗi nên cố tình tạo

Dữ liệu không nên sạch hoàn toàn. Cần tạo các case lỗi để hệ thống xử lý.

| Loại case | Số lượng đề xuất | Ý nghĩa |
|---|---:|---|
| Match đúng hoàn toàn | 30 | Hóa đơn có giao dịch tương ứng |
| Lệch ngày | 5 | Thanh toán sau hóa đơn 7–14 ngày |
| Lệch số tiền | 5 | Thanh toán thiếu/thừa |
| Không có giao dịch ngân hàng | 4 | Unmatched invoice |
| Giao dịch không có hóa đơn | 3 | Unmatched transaction |
| Trùng số hóa đơn | 2 | Duplicate invoice |
| OCR khó đọc | 5 | Ảnh nghiêng, mờ, layout khác |

Ví dụ:

```text
INV-2026-010:
Invoice total_amount = 8,800,000
Bank transaction amount = 8,500,000
=> Amount mismatch

INV-2026-014:
Có hóa đơn nhưng không có transaction
=> Unmatched invoice

TXN020:
Có giao dịch 12,000,000 nhưng không có invoice nào
=> Unmatched bank transaction

INV-2026-018:
Xuất hiện 2 lần
=> Duplicate invoice
```

---

## 12. Cách tạo input

### Cách 1: Tự tạo bằng template

Có thể dùng:

- Word
- Google Docs
- Canva
- HTML template
- Python script render HTML thành PDF

Nên tạo 5–10 layout khác nhau:

```text
Layout 1: hóa đơn đơn giản
Layout 2: có bảng sản phẩm dài
Layout 3: tiếng Việt không dấu
Layout 4: tiếng Anh
Layout 5: ảnh chụp bị nghiêng / hơi mờ
```

### Cách 2: Dùng public OCR dataset

Có thể dùng dataset receipt/invoice công khai để test OCR/document parsing.

Tuy nhiên public dataset chủ yếu giúp phần OCR/extraction. Phần bank reconciliation vẫn nên tự tạo bank statement CSV.

### Cách 3: Tạo fake invoice bằng code

Đây là cách nên ưu tiên.

Script Python cần làm:

```text
1. Tạo danh sách vendor giả
2. Tạo invoice number
3. Random ngày hóa đơn
4. Random line items
5. Tính subtotal, VAT, total
6. Render thành PDF bằng HTML
7. Sinh bank transaction tương ứng
8. Cố tình tạo mismatch/unmatched/duplicate
```

Ưu điểm:

```text
- Có thể tạo 50, 100, 500 hóa đơn nhanh
- Có ground truth để kiểm tra accuracy
- Không dính dữ liệu thật
- Dễ viết vào README
- Rất chuyên nghiệp
```

---

## 13. Feature chính của hệ thống

### 13.1. Upload hóa đơn

Người dùng upload:

- PDF invoice
- Ảnh hóa đơn
- File Excel/CSV bank statement
- File Excel/CSV vendor master

Sau khi upload, hệ thống tạo một processing job.

### 13.2. OCR & Data Extraction

Hệ thống tự đọc hóa đơn và lấy:

```text
invoice_number
vendor_name
vendor_tax_code
invoice_date
due_date
subtotal
vat_amount
total_amount
currency
line_items
```

### 13.3. Data Validation

Kiểm tra lỗi:

```text
- Thiếu số hóa đơn
- Thiếu ngày hóa đơn
- Tổng tiền không khớp với subtotal + VAT
- VAT âm
- Ngày hóa đơn nằm trong tương lai
- Hóa đơn bị trùng invoice_number
- Vendor chưa tồn tại trong master data
```

### 13.4. Bank Reconciliation

Match hóa đơn với giao dịch ngân hàng dựa trên:

```text
- Amount
- Date
- Vendor name
- Transfer description
- Invoice number
- Tax code
```

### 13.5. Exception Dashboard

Hiển thị các case cần xử lý:

```text
- Matched
- Partially matched
- Unmatched invoice
- Unmatched bank transaction
- Duplicate invoice
- Amount mismatch
- Vendor mismatch
- Suspicious transaction
```

### 13.6. AI Explanation

AI giải thích lỗi bằng ngôn ngữ tự nhiên.

Ví dụ:

```text
Hóa đơn INV-2026-018 chưa được match vì không có giao dịch ngân hàng nào trong khoảng ±7 ngày có số tiền tương ứng. Giao dịch gần nhất lệch 350.000 VND so với tổng hóa đơn.
```

---

## 14. Tech stack đề xuất

```text
Frontend: Next.js / React
Backend: FastAPI
Database: PostgreSQL
Queue: Celery + Redis
OCR: PaddleOCR / Tesseract
File Processing: pdfplumber, PyMuPDF, OpenCV, Pandas
Matching Engine: Python rules + fuzzy matching
AI Layer: LLM for explanation/report
Auth: JWT
Deployment: Docker Compose
Testing: Pytest
Logging: structlog / logging
```

---

## 15. Architecture

```text
User
 ↓
Next.js Frontend
 ↓
FastAPI Backend
 ↓
PostgreSQL Database
 ↓
Redis Queue
 ↓
Celery Worker
 ↓
OCR Service + Extraction Service
 ↓
Validation Engine
 ↓
Reconciliation Engine
 ↓
AI Explanation Service
 ↓
Dashboard / Report
```

### Vì sao cần Celery + Redis?

OCR và xử lý file có thể mất thời gian. Không nên để user upload file rồi API treo lâu.

Luồng đúng:

```text
User upload file
 ↓
Backend lưu file
 ↓
Backend tạo job
 ↓
Worker xử lý OCR ở background
 ↓
Frontend poll job status
 ↓
Khi xong thì hiển thị kết quả
```

---

## 16. Database schema

### 16.1. Bảng chính

```text
users
companies
vendors
uploaded_files
processing_jobs
invoices
invoice_items
bank_transactions
reconciliation_matches
reconciliation_exceptions
audit_logs
ai_reports
```

### 16.2. SQL schema mẫu

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    tax_code TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'analyst',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vendors (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    vendor_name TEXT NOT NULL,
    tax_code TEXT,
    bank_account TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE uploaded_files (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    user_id INT REFERENCES users(id),
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT,
    file_category TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE processing_jobs (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    file_id INT REFERENCES uploaded_files(id),
    job_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    vendor_id INT REFERENCES vendors(id),
    invoice_number TEXT NOT NULL,
    invoice_date DATE,
    due_date DATE,
    subtotal NUMERIC(18,2),
    vat_amount NUMERIC(18,2),
    total_amount NUMERIC(18,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'VND',
    status VARCHAR(50) DEFAULT 'pending',
    ocr_confidence NUMERIC(5,2),
    source_file_id INT REFERENCES uploaded_files(id),
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(company_id, invoice_number)
);

CREATE TABLE invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INT NOT NULL REFERENCES invoices(id),
    item_name TEXT,
    quantity NUMERIC(18,2),
    unit_price NUMERIC(18,2),
    line_total NUMERIC(18,2)
);

CREATE TABLE bank_transactions (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    transaction_id TEXT,
    transaction_date DATE NOT NULL,
    description TEXT,
    amount NUMERIC(18,2) NOT NULL,
    direction VARCHAR(20),
    bank_account TEXT,
    reference_code TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reconciliation_matches (
    id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES invoices(id),
    transaction_id INT REFERENCES bank_transactions(id),
    match_score NUMERIC(5,2),
    match_status VARCHAR(50),
    amount_diff NUMERIC(18,2),
    date_diff INT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reconciliation_exceptions (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    invoice_id INT REFERENCES invoices(id),
    transaction_id INT REFERENCES bank_transactions(id),
    exception_type VARCHAR(100),
    severity VARCHAR(20),
    message TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    user_id INT REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INT,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ai_reports (
    id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES companies(id),
    report_type TEXT,
    report_content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 17. Reconciliation logic

### 17.1. Matching score

Không nên match đơn giản bằng `amount == total_amount`.

Dùng scoring:

```text
Match Score =
    45% amount similarity
  + 25% date proximity
  + 20% vendor similarity
  + 10% invoice number/reference similarity
```

### 17.2. Match status

```text
score >= 85: matched
score 60–84: partially_matched
score < 60: unmatched
```

### 17.3. Python function mẫu

```python
from rapidfuzz import fuzz

def calculate_match_score(invoice, transaction):
    score = 0

    # Amount score
    amount_diff = abs(invoice.total_amount - abs(transaction.amount))
    if amount_diff == 0:
        score += 45
    elif amount_diff <= 5000:
        score += 35
    elif amount_diff <= 50000:
        score += 20

    # Date score
    date_diff = abs((transaction.transaction_date - invoice.invoice_date).days)
    if date_diff <= 3:
        score += 25
    elif date_diff <= 7:
        score += 15
    elif date_diff <= 14:
        score += 5

    # Vendor name score
    vendor_name = invoice.vendor_name or ""
    description = transaction.description or ""
    vendor_score = fuzz.partial_ratio(vendor_name.lower(), description.lower())
    score += vendor_score * 0.2

    # Invoice number in bank description
    if invoice.invoice_number and invoice.invoice_number in description:
        score += 10

    return min(score, 100)
```

---

## 18. Validation rules

### 18.1. Invoice validation

```text
- invoice_number is not null
- invoice_date is not null
- total_amount > 0
- subtotal + vat_amount = total_amount
- vat_amount >= 0
- invoice_date <= current_date
- vendor exists in vendor_master
- invoice_number is unique within company
```

### 18.2. Bank transaction validation

```text
- transaction_date is not null
- amount != 0
- direction in ['inflow', 'outflow']
- bank_account is not null
- transaction_id is unique
```

### 18.3. Exception severity

```text
Low: thiếu vendor name
Medium: chưa match transaction
High: lệch tiền lớn
Critical: duplicate invoice number
```

---

## 19. AI layer

Không để AI tự tính toán hoặc quyết định số liệu chính.

Python/SQL làm:

- OCR result parsing
- Validation
- Matching
- Exception classification
- KPI calculation

AI chỉ dùng để:

```text
1. Giải thích vì sao hóa đơn chưa match
2. Tóm tắt danh sách lỗi đối soát
3. Tạo báo cáo cuối ngày
4. Gợi ý hành động xử lý
5. Chuẩn hóa vendor name nếu bị viết khác nhau
```

### 19.1. Ví dụ AI explanation

```text
Hóa đơn INV-2026-018 chưa được match vì không có giao dịch ngân hàng nào trong khoảng ±7 ngày có số tiền tương ứng. Giao dịch gần nhất là TXN041, nhưng lệch 350.000 VND so với tổng hóa đơn.
```

### 19.2. Ví dụ AI daily report

```text
Trong ngày 26/06/2026, hệ thống xử lý 128 hóa đơn.

Kết quả:
- 104 hóa đơn đã match thành công
- 14 hóa đơn chưa tìm thấy giao dịch ngân hàng
- 6 hóa đơn có lệch số tiền
- 4 hóa đơn nghi ngờ trùng lặp

Vấn đề nghiêm trọng nhất là 6 hóa đơn của vendor ABC có tổng lệch 12.800.000 VND so với giao dịch ngân hàng.

Đề xuất:
- Ưu tiên kiểm tra các hóa đơn lệch tiền trên 1.000.000 VND
- Liên hệ vendor ABC để xác nhận lại số tiền thanh toán
- Kiểm tra lại nội dung chuyển khoản của các giao dịch không có số hóa đơn
```

---

## 20. Dashboard

### 20.1. Overview dashboard

Metrics:

```text
Total invoices processed
Matched rate
Unmatched invoices
Amount mismatch count
Duplicate invoices
Total unmatched value
OCR average confidence
```

### 20.2. Reconciliation dashboard

Columns:

```text
Invoice number
Vendor
Invoice amount
Matched transaction
Match score
Status
Exception reason
Action
```

### 20.3. Vendor dashboard

Metrics:

```text
Top vendors by invoice value
Vendors with most exceptions
Average payment delay
Duplicate invoice risk
```

---

## 21. API endpoints đề xuất

### Auth

```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

### Files

```http
POST /api/files/upload
GET  /api/files
GET  /api/files/{file_id}
```

### Jobs

```http
GET /api/jobs
GET /api/jobs/{job_id}
```

### Vendors

```http
POST /api/vendors/import
GET  /api/vendors
GET  /api/vendors/{vendor_id}
```

### Invoices

```http
POST /api/invoices/upload
GET  /api/invoices
GET  /api/invoices/{invoice_id}
PUT  /api/invoices/{invoice_id}
```

### Bank transactions

```http
POST /api/bank-transactions/import
GET  /api/bank-transactions
```

### Reconciliation

```http
POST /api/reconciliation/run
GET  /api/reconciliation/results
GET  /api/reconciliation/exceptions
POST /api/reconciliation/{match_id}/approve
POST /api/reconciliation/{match_id}/reject
```

### Reports

```http
POST /api/reports/generate
GET  /api/reports
GET  /api/reports/{report_id}
```

---

## 22. Folder structure

```text
invoice-automation-reconciliation/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── files.py
│   │   │   ├── invoices.py
│   │   │   ├── bank_transactions.py
│   │   │   ├── vendors.py
│   │   │   ├── reconciliation.py
│   │   │   └── reports.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── company.py
│   │   │   ├── vendor.py
│   │   │   ├── invoice.py
│   │   │   ├── bank_transaction.py
│   │   │   └── reconciliation.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── invoice.py
│   │   │   ├── vendor.py
│   │   │   ├── bank_transaction.py
│   │   │   └── reconciliation.py
│   │   │
│   │   ├── services/
│   │   │   ├── file_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── extraction_service.py
│   │   │   ├── validation_service.py
│   │   │   ├── reconciliation_service.py
│   │   │   └── ai_report_service.py
│   │   │
│   │   ├── workers/
│   │   │   └── tasks.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── Dockerfile
│
├── db/
│   ├── schema.sql
│   ├── seed.sql
│   └── sample_data/
│
├── scripts/
│   ├── generate_synthetic_data.py
│   ├── generate_invoice_pdfs.py
│   └── seed_database.py
│
├── notebooks/
│   ├── ocr_experiment.ipynb
│   ├── matching_experiment.ipynb
│   └── eda_bank_transactions.ipynb
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── api.md
│   └── demo_script.md
│
├── docker-compose.yml
├── README.md
├── .env.example
└── .gitignore
```

---

## 23. Roadmap implementation

### Phase 1: MVP

Mục tiêu: có thể demo end-to-end.

```text
- Upload invoice PDF/image
- OCR lấy text
- Parse invoice_number, vendor, date, total_amount
- Upload bank statement CSV
- Match invoice với transaction
- Hiển thị bảng kết quả
```

### Phase 2: Professional Backend

```text
- FastAPI structure chuẩn
- PostgreSQL schema
- Celery worker xử lý OCR
- Job status tracking
- Error handling
- Logging
```

### Phase 3: Reconciliation Engine

```text
- Matching score
- Fuzzy vendor matching
- Date tolerance
- Amount tolerance
- Duplicate detection
- Exception classification
```

### Phase 4: Dashboard

```text
- Overview metrics
- Match rate
- Exception list
- Vendor risk
- OCR confidence
```

### Phase 5: AI Layer

```text
- AI explain exception
- AI generate daily report
- AI suggest action
```

### Phase 6: Production polish

```text
- Docker Compose
- README đẹp
- Sample data
- Unit tests
- API docs
- Demo video
- CV bullet
```

---

## 24. MVP scope khuyên làm

Không nên làm quá rộng ngay từ đầu.

MVP chỉ cần:

```text
Input:
- 10 invoice PDF/image mẫu
- 1 file bank_statement.csv
- 1 file vendor_master.csv

Output:
- Extracted invoice table
- Bank transaction table
- Match result table
- Exception dashboard
- AI daily reconciliation report
```

Core flow:

```text
Upload → OCR → Extract → Validate → Match → Explain → Report
```

---

## 25. Các điểm làm project chuyên nghiệp hơn

### 25.1. OCR confidence score

Không tin OCR 100%.

```text
ocr_confidence < 80% → needs_review
ocr_confidence >= 80% → auto_process
```

### 25.2. Human-in-the-loop

Cho user sửa dữ liệu OCR trước khi reconcile.

Ví dụ:

```text
OCR extracted:
Vendor: Cong ty ABC
Amount: 12,500,000
Date: 2026-06-20

User có thể edit trước khi submit.
```

### 25.3. Audit log

Lưu mọi thao tác:

```text
User A uploaded invoice
System extracted data
System matched transaction
User B approved match
User C rejected match
```

### 25.4. Rule configuration

Cho admin cấu hình rule:

```text
Date tolerance: ±7 days
Amount tolerance: 5,000 VND
Auto-match threshold: 85
Manual-review threshold: 60
```

### 25.5. Exception severity

```text
Low: thiếu vendor name
Medium: chưa match transaction
High: lệch tiền lớn
Critical: duplicate invoice number
```

---

## 26. README note về synthetic data

Trong README nên ghi rõ:

```text
This project uses synthetic invoice and bank transaction data generated to simulate real-world finance operations while avoiding sensitive financial information.
```

Có thể viết thêm:

```text
The dataset includes intentionally created reconciliation exceptions such as duplicate invoices, amount mismatches, unmatched invoices, unmatched bank transactions, and OCR-noisy documents to evaluate the robustness of the system.
```

---

## 27. CV bullets

### Bản business + technical

```text
Built FinRecon AI, an invoice automation and bank reconciliation platform that extracts invoice data using OCR, validates financial records, matches invoices with bank transactions using rule-based scoring, detects reconciliation exceptions, and generates AI-assisted finance reports.
```

### Bản technical hơn

```text
Developed a production-style finance automation system using FastAPI, PostgreSQL, Celery, Redis, PaddleOCR, and React, featuring asynchronous document processing, OCR extraction, fuzzy transaction matching, exception management, and AI-generated reconciliation summaries.
```

### Skills

```text
Python
FastAPI
PostgreSQL
SQL
Pandas
OCR
Data validation
Reconciliation logic
Celery
Redis
React
Docker
AI integration
Business analytics
```

---

## 28. Prompt khởi động cho Codex

Dùng prompt này để bắt đầu với Codex:

```text
You are helping me build a portfolio-grade project called FinRecon AI – Invoice Automation & Bank Reconciliation Platform.

The project should be production-style and suitable for a Data Analyst / Data Scientist / Analytics Engineer portfolio.

Core workflow:
1. Generate synthetic vendors, invoices, bank transactions, and expected matches.
2. Render synthetic invoices into PDF files.
3. Build a FastAPI backend with PostgreSQL models for vendors, invoices, bank transactions, reconciliation matches, exceptions, processing jobs, and audit logs.
4. Build ingestion endpoints for vendor_master.csv, bank_statement.csv, and invoice PDF/image files.
5. Implement OCR/extraction service. For MVP, allow both OCR-based extraction and fallback extraction from synthetic metadata.
6. Implement validation rules for invoices and bank transactions.
7. Implement reconciliation engine using scoring:
   - 45% amount similarity
   - 25% date proximity
   - 20% vendor similarity
   - 10% invoice number/reference similarity
8. Classify results into matched, partially_matched, unmatched_invoice, unmatched_transaction, amount_mismatch, duplicate_invoice, vendor_mismatch.
9. Build dashboard endpoints for overview metrics and exception list.
10. Add AI report service that receives computed reconciliation results and produces a natural-language summary. AI must not calculate financial numbers; it only explains results computed by Python/SQL.
11. Add Docker Compose for backend, PostgreSQL, Redis, and Celery worker.
12. Add tests for matching logic and validation logic.
13. Add README, sample data, and demo instructions.

Please start by creating the repository structure, database models, and synthetic data generator. Prioritize an MVP that can run locally end-to-end.
```

---

## 29. Acceptance criteria

Project được xem là hoàn thành khi:

```text
1. Có thể tạo synthetic dataset bằng script.
2. Có thể tạo invoice PDF từ synthetic data.
3. Có thể import vendor_master.csv.
4. Có thể import bank_statement.csv.
5. Có thể upload/process invoice PDF.
6. Có thể extract thông tin invoice.
7. Có thể validate dữ liệu invoice.
8. Có thể reconcile invoice với bank transaction.
9. Có thể phân loại matched/unmatched/mismatch/duplicate.
10. Có dashboard metrics.
11. Có AI-generated report dựa trên kết quả đã tính.
12. Có Docker Compose chạy local.
13. Có README hướng dẫn chạy.
14. Có unit tests cho matching logic.
15. Có sample data để demo.
```

---

## 30. Kết luận

Dự án nên được xây theo hướng:

```text
Synthetic Data Generator
        ↓
Invoice PDF Generator
        ↓
FastAPI Backend
        ↓
PostgreSQL Data Model
        ↓
OCR / Extraction Service
        ↓
Validation Engine
        ↓
Reconciliation Engine
        ↓
Exception Dashboard
        ↓
AI Report
```

Đây là một project đủ mạnh để đưa vào CV vì nó thể hiện:

```text
- Business problem understanding
- Data engineering basics
- Data analysis automation
- Backend API design
- Database schema design
- OCR/document processing
- Matching algorithm
- Error handling
- AI integration
- Production-style software structure
```
