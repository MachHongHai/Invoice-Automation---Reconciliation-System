# FinRecon AI - Codex Handoff Context (Định hướng F&B / Nhà hàng)

Last updated: 2026-06-26

## Update moi nhat ve input mau va XML

- Khong bo XML hoan toan. XML hoa don dien tu Viet Nam duoc giu nhu nguon phu/sach cho nha cung cap chinh thuc, khong phai luong chinh.
- Luong chinh cua nha hang nho/F&B van la phieu nhap hang, anh/PDF bien nhan, bang ke thanh toan va sao ke ngan hang.
- `sample_inputs` da duoc cap nhat de generate:
  - `vat_einvoice` XML theo cau truc `HDon/DLHDon/TTChung/NBan/NMua/DSHHDVu/TToan`.
  - `sales_einvoice` XML cho hoa don ban hang.
  - `pos_receipt` va `vendor_pdf_receipt` cho OCR/fallback.
- Backend da co parser `parse_vietnam_einvoice_xml` trong `backend/app/utils.py`.
- Backend tu nhan dien file `.xml` trong luong upload invoice batch va endpoint rieng `POST /api/invoices/import-xml`.
- Frontend da cho phep chon `.xml` trong upload phieu nhap hang.
- Frontend co muc moi `Du lieu mau` de generate sample tu giao dien.
- Backend co endpoint:
  - `POST /api/sample-data/generate?clear_existing=true|false`
  - `DELETE /api/sample-data/generated`
- Sample generated files khong con duoc giu trong `sample_inputs/raw`/`processed`. API generate tao file tam, nap vao bang `sample_generated_files`, sau do xoa file vat ly.
- Download sample:
  - `GET /api/sample-data/files`
  - `GET /api/sample-data/files/{file_id}/download`
  - `GET /api/sample-data/files/download.zip`
- Anh/PDF sample hoa don ban hang da doi sang layout giong anh mau nguoi dung gui: header ten cua hang, tieu de `HOA DON BAN HANG`, bang 10 dong voi cot `STT`, `TEN HANG`, `SO LUONG`, `DON GIA`, `THANH TIEN`, dong `CONG`, thanh tien va chu ky.

## Định vị dự án (Project Positioning)

Tên dự án:
```text
FinRecon AI - Hệ thống Đối soát & Kiểm soát Hóa đơn tự động cho Nhà hàng (F&B)
```

### Các định hướng cốt lõi mới (F&B / SME Focus):
1. **OCR-First đối với Phiếu Nhập Hàng**: Hỗ trợ quét ảnh chụp hoặc file PDF của các phiếu giao hàng, hóa đơn chợ lẻ bằng thư viện **EasyOCR** tích hợp trực tiếp ở Backend.
2. **Tự động sinh mã hóa đơn**: Các phiếu giao hàng viết tay ở chợ thường không có số hóa đơn (`invoice_number`). Hệ thống tự động sinh mã dạng `REC-MMDD-XXXX` (với `XXXX` là số ngẫu nhiên) để tránh bị chặn ở bước Validation.
3. **Đối soát gộp 1-to-N (Consolidated Payments)**: Cho phép đối soát 1 giao dịch ngân hàng khớp với tổng tiền của nhiều phiếu nhập hàng chưa thanh toán thuộc cùng một nhà cung cấp trong tuần/tháng.
4. **Fuzzy Matching nâng cao**: Loại bỏ stop-words tiếng Việt thông dụng khi đối soát nội dung chuyển khoản (như "ck", "tien", "thanh toan", "cho", "mua") và chuẩn hóa không dấu (unaccent) nhằm tối ưu hóa độ chính xác đối soát tên mối buôn viết tắt/dân dã (ví dụ: "ck tien thit chi lan" khớp với "Chị Lan Mối Thịt").
5. **Đồng bộ thông tin ngân hàng Mối buôn**: Bổ sung trường **Tên chủ tài khoản (`bank_account_holder`)** viết hoa không dấu (ví dụ: `NGUYEN THI LAN`) để tăng tính xác thực cho luồng chuyển tiền và đối soát.
6. **Giao diện 100% Tiếng Việt**: Trải nghiệm UI trực quan, gần gũi với kế toán nhà hàng (đổi tên các thuật ngữ chuyên ngành sang tiếng Việt).
7. **Loại bỏ hoàn toàn XML**: Đã lược bỏ mọi tính năng nhập hóa đơn điện tử XML (E-Invoicing) của doanh nghiệp lớn khỏi cả backend, frontend và bộ sinh dữ liệu mẫu.

---

## Quy trình nghiệp vụ mới (8 Bước)

Giao diện hệ thống tuân theo luồng công việc 8 bước chuẩn hóa bằng tiếng Việt:

1. **Cấu hình Luật Đối soát**: Thiết lập các tham số dung sai số tiền (tolerance), ngưỡng điểm khớp tự động, ngưỡng điểm cần duyệt tay.
2. **Danh mục Mối buôn (Vendor Master)**: Import danh sách các nhà cung cấp, mối buôn chợ (ví dụ: Chị Lan Mối Thịt, Bác Hải Rau Củ) kèm thông tin tài khoản ngân hàng đầy đủ: **Ngân hàng, Số tài khoản, Tên chủ tài khoản**.
3. **Nguồn phiếu nhập hàng**: Upload ảnh chụp hóa đơn in nhiệt từ máy POS (`.png` tự động chạy EasyOCR) hoặc tệp Hóa đơn điện tử VAT (`.pdf`). Hỗ trợ **Sửa Nhanh (Quick Edit)** trực tiếp thông tin tiền/tên mối buôn trên lưới nếu OCR nhận diện sai. Có hiển thị **Độ tin cậy OCR**.
4. **Kiểm tra phiếu nhập (Validation)**: Chạy công cụ kiểm tra tính hợp lệ trước khi duyệt chi. Chuyển trạng thái phiếu nhập sang "Đã duyệt" để đưa vào danh sách thanh toán.
5. **Bảng kê thanh toán**: Tự động gom các phiếu nhập đã duyệt thành bảng kê thanh toán chi tiết theo từng mối buôn.
6. **Import Sao kê Ngân hàng (Bank Statement)**: Import tệp sao kê tài khoản ngân hàng của nhà hàng dưới dạng Excel/CSV.
7. **Đối soát tự động (Reconciliation)**: Thực hiện đối soát thông minh (hỗ trợ so khớp 1-to-N). Bảng kết quả hiển thị chi tiết tên mối buôn, số tiền hóa đơn và số tiền chuyển khoản thực tế. Phân loại các giao dịch thành: khớp hoàn toàn, khớp cần duyệt tay, lệch tiền hoặc đưa vào danh sách Ngoại lệ (Exceptions).
8. **Báo cáo & Dashboard**: Xem báo cáo tổng quan kết quả đối soát kèm chỉ số **Tổng giá trị tiền hàng** và **Giá trị tiền đã đối soát**. Kiểm tra vết log và xuất dữ liệu đối soát ra Excel.

---

## Cách chạy dự án

### Backend:
```powershell
cd "D:\Du-an\Invoice Automation & Reconciliation System\backend"
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
*Tài liệu API (Swagger UI):* `http://127.0.0.1:8000/docs`

### Frontend:
```powershell
cd "D:\Du-an\Invoice Automation & Reconciliation System\frontend"
npm run dev
```
*Địa chỉ ứng dụng:* `http://127.0.0.1:5173`

---

## Tài khoản Đăng nhập Demo

Sử dụng mật khẩu chung **`demo123`** cho các tài khoản:
- Kế toán trưởng / Admin: `admin@finrecon.local`
- Nhân viên kiểm tra: `reviewer@finrecon.local`
- Kế toán viên: `accountant@finrecon.local`

---

## Sơ đồ cấu trúc dữ liệu Backend

Các bảng chính trong SQLite (`backend/data/finrecon.db`):
- `vendors`: Danh mục mối buôn (tên mối buôn, tài khoản ngân hàng, tên chủ tài khoản, ngân hàng, địa chỉ, email/sđt, trạng thái).
- `invoices`: Phiếu nhập hàng (lưu thông tin OCR, số tiền, mối buôn, mã phiếu tự sinh).
- `bank_transactions`: Sao kê ngân hàng (ngày giao dịch, số tiền, nội dung chuyển khoản).
- `payment_batches`: Danh sách các khoản thanh toán dự kiến.
- `reconciliation_matches`: Kết quả đối soát (bao gồm liên kết 1-to-N giữa giao dịch ngân hàng và các phiếu nhập).
- `reconciliation_exceptions`: Các trường hợp lệch tiền hoặc không tìm thấy mối buôn cần xử lý tay.

---

## Bộ dữ liệu mẫu sinh tự động (Sample Inputs)

Script sinh dữ liệu mẫu tạo ra các file input chuẩn ngoài đời:
- **POS Printed Receipts (`.png` - 25 file)**: Phiếu thanh toán in từ máy POS hoặc ảnh chụp bằng điện thoại chứa Store Header, danh mục thực phẩm F&B, tổng cộng tiền hàng, số tài khoản của mối buôn.
- **VAT E-Invoices (`.pdf` - 25 file)**: Hóa đơn điện tử chính thức thiết kế chuyên nghiệp, ghi rõ thông tin Seller, Buyer, và thuế suất VAT.
- Các file mẫu đều chứa từ khóa tiếng Việt như `Nha cung cap`, `Cong tien hang`, `Tong cong` giúp kiểm thử EasyOCR nhận dạng chính xác 100%.

Cách chạy bộ sinh dữ liệu mẫu:
```powershell
cd "D:\Du-an\Invoice Automation & Reconciliation System\sample_inputs\scripts"
..\..\backend\.venv\Scripts\python.exe generate_all_inputs.py
```
