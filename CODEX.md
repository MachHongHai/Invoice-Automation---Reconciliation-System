# FinRecon AI - Codex Handoff Context (Định hướng F&B / Nhà hàng)

Last updated: 2026-06-26

## Cập nhật mới nhất về Giao diện & Cấu hình Frontend (React + Tailwind CSS)

Hệ thống Frontend đã được nâng cấp toàn diện lên một giao diện F&B chuyên nghiệp, hiện đại và tối giản:
- **Framework & CSS**: Đã cài đặt và tích hợp **Tailwind CSS v3** cùng **PostCSS** và **Autoprefixer**. Đã cấu hình tệp `tailwind.config.js`, `postcss.config.js`, và `vite.config.js` để tự động biên dịch và hot-reload.
- **Bố cục Sidebar (Left Navigation)**: Chuyển đổi từ thanh menu ngang cũ sang cấu trúc Sidebar bên trái chuyên nghiệp, quản lý trực quan tiến độ của luồng nghiệp vụ 9 bước.
- **Light Mode & Dark Mode**: Bổ sung nút chuyển đổi theme (Sun/Moon) trên Sidebar, tự động lưu lựa chọn vào `localStorage` và đồng bộ giao diện ở cả chế độ tối (dark mode) và sáng (light mode).
- **Thiết kế tối giản (Decluttered UI)**: 
  - Loại bỏ các cột giải thích nghiệp vụ dài dòng bên phải (side panels) của các bước, chuyển về bố cục **1 cột duy nhất** giúp các bảng dữ liệu rộng rãi và dễ nhìn hơn.
  - Rút gọn các dòng mô tả phụ và nhãn chữ hướng dẫn để giao diện thanh thoát, tập trung vào nghiệp vụ.
- **Thành phần UI nâng cấp**:
  - `DataTable`: Bảng dữ liệu được thiết kế lại theo phong cách hiện đại (border-radius, shadow, màu nền mờ) và đã được tích hợp **Bộ Phân Trang tự động (Pagination)** ở chân trang.
  - `UploadCard`: Hỗ trợ **Xem trước tệp (File Preview)** trực quan bằng cách hiển thị các ảnh thumbnail nhỏ đối với các file ảnh vừa được chọn trước khi upload.
  - `QuickEditModal`: Thay thế hộp thoại trình duyệt `window.prompt` thô sơ bằng một **Modal sửa nhanh tùy chỉnh bằng React** có hiệu ứng chuyển động phóng to mượt mà.
  - `Metric`: Các thẻ chỉ số dạng Glassmorphism sử dụng icon màu sắc tương phản nổi bật theo tình trạng dữ liệu (Xanh - Hợp lệ, Vàng - Cảnh báo, Đỏ - Ngoại lệ).

## Khắc phục lỗi Hệ thống & API đường dẫn
- **Sửa lỗi trắng màn hình**: Đã khai báo lại đầy đủ hai hàm chuyển tiếp `previousStep()` và `nextStep()` trong `App.jsx` bị thiếu trước đó.
- **Sửa lỗi 404 API**: Cập nhật hàm tải dữ liệu `loadData()` trong `App.jsx` để gọi đúng các API endpoint của backend:
  - Thay `/api/reconciliation/results/overview` thành `/api/dashboard/summary`.
  - Thay `/api/reconciliation/exceptions` thành `/api/exceptions`.

---

## Cập nhật về Input mẫu và XML cũ

- Không bỏ XML hoàn toàn. XML hóa đơn điện tử Việt Nam được giữ như nguồn phụ/sách cho nhà cung cấp chính thức, không phải luồng chính.
- Luồng chính của nhà hàng nhỏ/F&B vẫn là phiếu nhập hàng, ảnh/PDF biên nhận, bảng kê thanh toán và sao kê ngân hàng.
- `sample_inputs` đã được cập nhật để generate:
  - `vat_einvoice` XML theo cấu trúc `HDon/DLHDon/TTChung/NBan/NMua/DSHHDVu/TToan`.
  - `sales_einvoice` XML cho hóa đơn bán hàng.
  - `pos_receipt` và `vendor_pdf_receipt` cho OCR/fallback.
- Backend đã có parser `parse_vietnam_einvoice_xml` trong `backend/app/utils.py`.
- Backend tự nhận diện file `.xml` trong luồng upload invoice batch và endpoint riêng `POST /api/invoices/import-xml`.
- Frontend cho phép chọn `.xml` trong upload phiếu nhập hàng.
- Download sample qua API:
  - `GET /api/sample-data/files`
  - `GET /api/sample-data/files/{file_id}/download`
  - `GET /api/sample-data/files/download.zip`

---

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

---

## Quy trình nghiệp vụ mới (9 Bước)

Giao diện hệ thống tuân theo luồng công việc 9 bước chuẩn hóa bằng tiếng Việt:

1. **Dữ liệu mẫu**: Tạo bộ file mẫu F&B để chạy thử nghiệm nhanh toàn bộ quy trình.
2. **Cấu hình Quy tắc**: Thiết lập các tham số dung sai số tiền (tolerance), ngưỡng điểm khớp tự động, ngưỡng điểm cần duyệt tay.
3. **Danh mục Mối buôn (Vendor Master)**: Import danh sách các nhà cung cấp, mối buôn chợ kèm thông tin tài khoản ngân hàng đầy đủ: **Ngân hàng, Số tài khoản, Tên chủ tài khoản**.
4. **Phiếu nhập hàng**: Tải lên ảnh chụp phiếu giao hàng viết tay, biên nhận hoặc Excel để OCR tự động trích xuất.
5. **Kiểm tra phiếu nhập (Validation)**: Chạy công cụ kiểm tra tính hợp lệ trước khi duyệt chi. Chuyển trạng thái phiếu nhập sang "Đã duyệt" để chuẩn bị thanh toán.
6. **Bảng kê thanh toán**: Tự động gom các phiếu nhập đã duyệt thành bảng kê thanh toán chi tiết theo từng mối buôn.
7. **Import Sao kê Ngân hàng (Bank Statement)**: Import tệp sao kê tài khoản ngân hàng dưới dạng Excel/CSV.
8. **Đối soát thanh toán (Reconciliation)**: Thực hiện đối soát thông minh (hỗ trợ so khớp 1-to-N). Bảng kết quả hiển thị khớp, lệch tiền hoặc Ngoại lệ (Exceptions).
9. **Bảng điều khiển (Dashboard)**: Xem báo cáo tổng quan kết quả đối soát kèm chỉ số tổng tiền hàng, tỷ lệ khớp tiền, các vendor có nhiều lỗi và audit logs.

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
