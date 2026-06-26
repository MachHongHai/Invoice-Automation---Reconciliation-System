import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  Banknote,
  CheckCircle2,
  ClipboardCheck,
  FileSpreadsheet,
  FileText,
  History,
  RefreshCw,
  Settings2,
  Upload,
  WandSparkles,
} from "lucide-react";

const API_BASE =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.hostname || "127.0.0.1"}:8000`;

const defaultRules = {
  auto_match_threshold: 85,
  manual_review_threshold: 60,
  date_tolerance_days: 30,
  amount_tolerance_vnd: 500000,
  low_ocr_confidence_threshold: 80,
  vat_tolerance: 1,
};

const statusLabels = {
  pending: "Đang chờ",
  processing: "Đang xử lý",
  completed: "Hoàn tất",
  completed_with_errors: "Có lỗi",
  failed: "Thất bại",
  valid: "Hợp lệ",
  invalid: "Không hợp lệ",
  validated: "Đã kiểm soát",
  imported: "Đã import",
  parsed: "Đã parse",
  needs_review: "Cần kiểm tra",
  reviewed: "Đã review",
  rejected: "Từ chối",
  approved_for_payment: "Đã duyệt thanh toán",
  payment_scheduled: "Đã lên lịch trả",
  paid: "Đã thanh toán",
  reconciled: "Đã đối soát",
  matched: "Đã khớp",
  partially_matched: "Cần review",
  amount_mismatch: "Lệch tiền",
  unmatched_invoice: "Hóa đơn chưa thanh toán",
  unmatched_approved_invoice: "Duyệt nhưng chưa thanh toán",
  unmatched_transaction: "Giao dịch thiếu hóa đơn",
  unmatched_bank_transaction: "Giao dịch thiếu payment",
  duplicate_invoice: "Hóa đơn trùng",
  vendor_not_found: "Không có vendor",
  vendor_bank_mismatch: "Sai tài khoản vendor",
  vendor_mismatch: "Sai vendor",
  unusual_amount: "Số tiền bất thường",
  date_mismatch: "Lệch ngày",
  missing_required_field: "Thiếu dữ liệu",
  low_ocr_confidence: "OCR thấp",
  open: "Mở",
  in_review: "Đang xử lý",
  resolved: "Đã xử lý",
  dismissed: "Bỏ qua",
  low: "Thấp",
  medium: "Trung bình",
  high: "Cao",
  critical: "Nghiêm trọng",
  inflow: "Tiền vào",
  outflow: "Tiền ra",
};

const steps = [
  {
    id: "sample-data",
    number: 1,
    label: "Dữ liệu mẫu",
    short: "Sample",
    icon: FileText,
    objective: "Tạo bộ file mẫu F&B để test nhanh toàn bộ quy trình.",
  },
  {
    id: "rules",
    number: 2,
    label: "Cấu hình quy tắc",
    short: "Quy tắc",
    icon: Settings2,
    objective: "Thiết lập ngưỡng kiểm soát và dung sai cho nhà hàng.",
  },
  {
    id: "vendors",
    number: 3,
    label: "Danh mục mối buôn",
    short: "Mối buôn",
    icon: FileSpreadsheet,
    objective: "Quản lý danh sách các mối buôn, nhà cung cấp thực phẩm.",
  },
  {
    id: "invoice-source",
    number: 4,
    label: "Phiếu nhập hàng",
    short: "Nhập hàng",
    icon: Upload,
    objective: "Tải lên ảnh chụp phiếu giao hàng viết tay, biên nhận.",
  },
  {
    id: "prepayment",
    number: 5,
    label: "Kiểm tra phiếu nhập",
    short: "Kiểm tra",
    icon: ClipboardCheck,
    objective: "Kiểm tra lại dữ liệu hóa đơn, sửa lỗi OCR và duyệt.",
  },
  {
    id: "payment",
    number: 6,
    label: "Bảng kê thanh toán",
    short: "Bảng kê",
    icon: Banknote,
    objective: "Lập bảng kê các phiếu cần thanh toán cho mối buôn.",
  },
  {
    id: "bank",
    number: 7,
    label: "Sao kê ngân hàng",
    short: "Sao kê",
    icon: FileSpreadsheet,
    objective: "Tải lên sao kê tài khoản ngân hàng để đối soát.",
  },
  {
    id: "reconcile",
    number: 8,
    label: "Đối soát thanh toán",
    short: "Đối soát",
    icon: AlertTriangle,
    objective: "Tự động gộp và khớp tiền chuyển khoản với các phiếu nhập.",
  },
  {
    id: "dashboard",
    number: 9,
    label: "Bảng điều khiển",
    short: "Báo cáo",
    icon: WandSparkles,
    objective: "Xem báo cáo tổng quan về tình hình công nợ và thanh toán.",
  },
];

function formatMoney(value, currency = "VND") {
  if (value === null || value === undefined || value === "") return "-";
  return `${new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 0 }).format(Number(value))} ${currency}`;
}

function StatusPill({ value }) {
  const key = String(value || "pending").toLowerCase();
  return <span className={`pill ${key.replaceAll("_", "-")}`}>{statusLabels[key] || value || "Đang chờ"}</span>;
}

function Metric({ icon: Icon, label, value, tone }) {
  return (
    <section className={`metric ${tone || ""}`}>
      <Icon size={18} aria-hidden="true" />
      <span>{label}</span>
      <strong>{value}</strong>
    </section>
  );
}

function DataTable({ columns, rows, empty = "Chưa có dữ liệu" }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td className="empty-row" colSpan={columns.length}>
                {empty}
              </td>
            </tr>
          ) : (
            rows.map((row, index) => (
              <tr key={row.id || `${row.invoice_id || row.transaction_id || row.payment_id || "row"}-${index}`}>
                {columns.map((column) => (
                  <td key={column.key}>{column.render ? column.render(row) : row[column.key] || "-"}</td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

function Field({ label, name, value, onChange, type = "text" }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input type={type} name={name} value={value ?? ""} onChange={onChange} />
    </label>
  );
}

function UploadCard({ icon: Icon, title, helper, inputRef, accept, multiple, onSubmit, primary }) {
  return (
    <div className={`upload-box ${primary ? "primary-source" : ""}`}>
      <Icon size={24} />
      <strong>{title}</strong>
      <p>{helper}</p>
      <input ref={inputRef} type="file" accept={accept} multiple={multiple} />
      <button onClick={onSubmit}>Tải lên</button>
    </div>
  );
}

export default function App() {
  const [activeStep, setActiveStep] = useState("sample-data");
  const [overview, setOverview] = useState({});
  const [vendors, setVendors] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [paymentBatches, setPaymentBatches] = useState([]);
  const [matches, setMatches] = useState([]);
  const [exceptions, setExceptions] = useState([]);
  const [batches, setBatches] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [rules, setRules] = useState(defaultRules);
  const [auditLogs, setAuditLogs] = useState([]);
  const [reports, setReports] = useState([]);
  const [reportText, setReportText] = useState("");
  const [sampleSummary, setSampleSummary] = useState(null);
  const [sampleFiles, setSampleFiles] = useState([]);
  const [clearGeneratedBeforeRun, setClearGeneratedBeforeRun] = useState(true);
  const [authToken, setAuthToken] = useState(() => localStorage.getItem("finrecon_token") || "");
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("finrecon_user") || "null");
    } catch {
      return null;
    }
  });
  const [loginForm, setLoginForm] = useState({ email: "admin@finrecon.local", password: "demo123" });
  const [exceptionDrafts, setExceptionDrafts] = useState({});
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");

  const vendorFileRef = useRef(null);
  const invoiceRegisterRef = useRef(null);
  const attachmentFileRef = useRef(null);
  const paymentFileRef = useRef(null);
  const bankFileRef = useRef(null);
  const fallbackFilesRef = useRef(null);

  const active = steps.find((step) => step.id === activeStep) || steps[0];
  const activeIndex = steps.findIndex((step) => step.id === activeStep);

  const reviewInvoices = useMemo(
    () => invoices.filter((invoice) => ["needs_review", "invalid", "rejected"].includes(invoice.status) || invoice.validation_status !== "valid"),
    [invoices],
  );
  const approvedInvoices = useMemo(
    () => invoices.filter((invoice) => ["approved_for_payment", "payment_scheduled", "paid", "reconciled"].includes(invoice.status)),
    [invoices],
  );

  async function request(path, options = {}) {
    const headers = {
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
      ...(options.headers || {}),
    };
    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    } catch (error) {
      throw new Error(`Không kết nối được backend tại ${API_BASE}. Hãy chạy backend bằng npm run dev trong thư mục backend.`);
    }
    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || `Request failed: ${response.status}`);
    }
    return response.json();
  }

  async function refresh() {
    const [
      nextOverview,
      nextVendors,
      nextInvoices,
      nextTransactions,
      nextPayments,
      nextMatches,
      nextExceptions,
      nextBatches,
      nextJobs,
      nextRules,
      nextAuditLogs,
      nextReports,
      nextSampleFiles,
    ] = await Promise.all([
      request("/api/dashboard/summary"),
      request("/api/vendors"),
      request("/api/invoices"),
      request("/api/bank-transactions"),
      request("/api/payment-batches"),
      request("/api/reconciliation/results"),
      request("/api/exceptions"),
      request("/api/batches"),
      request("/api/jobs"),
      request("/api/rules"),
      request("/api/audit-logs"),
      request("/api/reports"),
      request("/api/sample-data/files"),
    ]);
    setOverview(nextOverview);
    setVendors(nextVendors);
    setInvoices(nextInvoices);
    setTransactions(nextTransactions);
    setPaymentBatches(nextPayments);
    setMatches(nextMatches);
    setExceptions(nextExceptions);
    setBatches(nextBatches);
    setJobs(nextJobs);
    setRules({ ...defaultRules, ...nextRules });
    setAuditLogs(nextAuditLogs);
    setReports(nextReports);
    setSampleFiles(nextSampleFiles);
  }

  useEffect(() => {
    refresh().catch((error) => setNotice(error.message));
  }, []);

  async function withBusy(action, successMessage) {
    setBusy(true);
    setNotice("");
    try {
      const result = await action();
      await refresh();
      setNotice(successMessage);
      return result;
    } catch (error) {
      setNotice(error.message);
      return null;
    } finally {
      setBusy(false);
    }
  }

  async function login(event) {
    event.preventDefault();
    await withBusy(async () => {
      const result = await request("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginForm),
      });
      setAuthToken(result.access_token);
      setCurrentUser(result.user);
      localStorage.setItem("finrecon_token", result.access_token);
      localStorage.setItem("finrecon_user", JSON.stringify(result.user));
    }, "Đã đăng nhập");
  }

  function logout() {
    setAuthToken("");
    setCurrentUser(null);
    localStorage.removeItem("finrecon_token");
    localStorage.removeItem("finrecon_user");
  }

  async function importFile(file, endpoint, label) {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    await withBusy(() => request(endpoint, { method: "POST", body: form }), `Đã nhập ${label}`);
  }


  async function uploadFallback(files) {
    if (!files?.length) return;
    const form = new FormData();
    [...files].forEach((file) => form.append("files", file));
    await withBusy(() => request("/api/batches/invoices/upload", { method: "POST", body: form }), "Đã upload fallback OCR");
  }

  async function uploadAttachment(file) {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    await withBusy(() => request("/api/invoices/upload-attachment", { method: "POST", body: form }), "Đã upload attachment");
  }

  async function runValidation() {
    await withBusy(() => request("/api/validation/run", { method: "POST" }), "Đã chạy kiểm soát trước thanh toán");
  }

  async function approveInvoice(invoice) {
    const key = invoice.invoice_id || invoice.id;
    await withBusy(() => request(`/api/invoices/${key}/approve`, { method: "POST" }), "Đã duyệt hóa đơn");
  }

  async function rejectInvoice(invoice) {
    const key = invoice.invoice_id || invoice.id;
    await withBusy(() => request(`/api/invoices/${key}/reject`, { method: "POST" }), "Đã từ chối hóa đơn");
  }

  async function generatePaymentBatch() {
    await withBusy(
      () => request("/api/payment-batches/generate-from-approved-invoices", { method: "POST" }),
      "Đã sinh payment batch từ hóa đơn đã duyệt",
    );
  }

  async function runReconciliation() {
    await withBusy(() => request("/api/reconciliation/run", { method: "POST" }), "Đã chạy đối soát");
  }

  async function approveMatch(matchId) {
    await withBusy(() => request(`/api/reconciliation/${matchId}/approve`, { method: "POST" }), "Đã duyệt match");
  }

  async function rejectMatch(matchId) {
    await withBusy(() => request(`/api/reconciliation/${matchId}/reject`, { method: "POST" }), "Đã từ chối match");
  }

  async function updateException(exceptionId, fallbackStatus) {
    const draft = exceptionDrafts[exceptionId] || {};
    await withBusy(
      () =>
        request(`/api/exceptions/${exceptionId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            status: draft.status || fallbackStatus || "in_review",
            note: draft.note || "",
            resolved: (draft.status || fallbackStatus) === "resolved",
          }),
        }),
      "Đã cập nhật ngoại lệ",
    );
  }

  async function saveRules(event) {
    event.preventDefault();
    await withBusy(
      () =>
        request("/api/rules", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(rules),
        }),
      "Đã lưu cấu hình rule",
    );
  }

  async function generateReport() {
    const result = await withBusy(() => request("/api/reports/generate", { method: "POST" }), "Đã tạo báo cáo");
    if (result?.report) setReportText(result.report);
  }

  async function clearGeneratedSamples() {
    const result = await withBusy(
      () => request("/api/sample-data/generated", { method: "DELETE" }),
      "Đã xóa các file sample đã generate",
    );
    if (result) setSampleSummary({ cleared: true, ...result });
  }

  async function generateSamples() {
    const result = await withBusy(
      () => request(`/api/sample-data/generate?clear_existing=${clearGeneratedBeforeRun}`, { method: "POST" }),
      "Đã generate bộ dữ liệu mẫu",
    );
    if (result) setSampleSummary(result);
  }

  async function quickEditInvoice(invoice) {
    const newAmount = window.prompt("Nhập tổng tiền mới (VND):", invoice.total_amount || "");
    const newVendor = window.prompt("Nhập tên mối buôn mới:", invoice.vendor_name || "");
    
    if (newAmount !== null && newVendor !== null) {
      await withBusy(() => request(`/api/invoices/${invoice.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...invoice,
          total_amount: Number(newAmount),
          vendor_name: newVendor,
          status: "needs_review",
          validation_status: "pending"
        })
      }), "Đã sửa nhanh phiếu nhập");
    }
  }

  function nextStep() {
    setActiveStep(steps[Math.min(activeIndex + 1, steps.length - 1)].id);
  }

  function previousStep() {
    setActiveStep(steps[Math.max(activeIndex - 1, 0)].id);
  }

  function renderTopAuth() {
    return currentUser ? (
      <div className="user-box">
        <span>{currentUser.email}</span>
        <strong>{currentUser.role}</strong>
        <button onClick={logout}>Đăng xuất</button>
      </div>
    ) : (
      <form className="login-box" onSubmit={login}>
        <input value={loginForm.email} onChange={(event) => setLoginForm({ ...loginForm, email: event.target.value })} />
        <input type="password" value={loginForm.password} onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })} />
        <button type="submit">Đăng nhập</button>
      </form>
    );
  }

  return (
    <main className="app-shell workflow-shell">
      <aside className="sidebar workflow-sidebar">
        <div className="brand">
          <Banknote size={24} />
          <div>
            <strong>FinRecon AI</strong>
            <span>Invoice Control & Payment Reconciliation</span>
          </div>
        </div>
        <nav className="step-nav">
          {steps.map(({ id, number, label, short, icon: Icon }) => (
            <button key={id} className={activeStep === id ? "active" : ""} onClick={() => setActiveStep(id)}>
              <span className="step-number">{number}</span>
              <Icon size={16} />
              <span>
                <strong>{label}</strong>
                <em>{short}</em>
              </span>
            </button>
          ))}
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar workflow-topbar">
          <div>
            <p>Bước {active.number} trong {steps.length}</p>
            <h1>{active.label}</h1>
            <span>{active.objective}</span>
          </div>
          <div className="top-actions">
            {renderTopAuth()}
            <button className="icon-button" onClick={() => refresh()} disabled={busy} title="Làm mới dữ liệu">
              <RefreshCw size={18} />
            </button>
          </div>
        </header>

        <div className="workflow-progress">
          {steps.map((step, index) => (
            <button
              key={step.id}
              className={`${index < activeIndex ? "done" : ""} ${index === activeIndex ? "current" : ""}`}
              onClick={() => setActiveStep(step.id)}
            >
              {step.number}
            </button>
          ))}
        </div>

        {notice && <div className="notice">{notice}</div>}

        {activeStep === "sample-data" && (
          <section className="step-layout">
            <section className="panel">
              <div className="section-head">
                <div>
                  <h2>Tạo dữ liệu mẫu</h2>
                  <p className="helper-text">Sinh bộ file mẫu cho nhà hàng nhỏ: mối buôn, phiếu nhập hàng theo mẫu hóa đơn bán hàng, XML hóa đơn điện tử, bảng kê thanh toán và sao kê ngân hàng.</p>
                </div>
                <div className="row-actions">
                  <button onClick={generateSamples} disabled={busy}>Generate sample</button>
                  <button onClick={clearGeneratedSamples} disabled={busy}>Xóa sample trong DB</button>
                  <a className={`button-link ${sampleFiles.length ? "" : "disabled"}`} href={`${API_BASE}/api/sample-data/files/download.zip`}>Tải tất cả ZIP</a>
                </div>
              </div>
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={clearGeneratedBeforeRun}
                  onChange={(event) => setClearGeneratedBeforeRun(event.target.checked)}
                />
                <span>Xóa toàn bộ sample hiện tại trong database trước khi tạo mới</span>
              </label>
              <div className="metrics-grid compact">
                <Metric icon={FileSpreadsheet} label="Mối buôn" value={sampleSummary?.vendors ?? "-"} />
                <Metric icon={FileText} label="Phiếu nhập" value={sampleSummary?.invoices ?? "-"} />
                <Metric icon={FileText} label="XML HĐĐT" value={(sampleSummary?.einvoice_xml_files ?? sampleFiles.filter((file) => file.file_category === "einvoice_xml").length) || "-"} />
                <Metric icon={Upload} label="Ảnh/PDF phiếu" value={((sampleSummary?.image_files ?? sampleFiles.filter((file) => file.file_category === "invoice_image").length) + (sampleSummary?.pdf_files ?? sampleFiles.filter((file) => file.file_category === "invoice_pdf").length)) || "-"} />
                <Metric icon={ClipboardCheck} label="Bảng kê" value={sampleSummary?.payments ?? "-"} />
                <Metric icon={Banknote} label="Sao kê" value={sampleSummary?.transactions ?? "-"} />
              </div>
              <DataTable
                rows={sampleFiles}
                empty="Chưa có sample trong database"
                columns={[
                  { key: "file_name", label: "Tên file" },
                  { key: "file_category", label: "Loại" },
                  { key: "file_size", label: "Dung lượng", render: (row) => `${Math.ceil((row.file_size || 0) / 1024)} KB` },
                  { key: "relative_path", label: "Đường dẫn logic" },
                  {
                    key: "download",
                    label: "Tải về",
                    render: (row) => <a className="button-link compact-link" href={`${API_BASE}${row.download_url}`}>Tải</a>,
                  },
                ]}
              />
            </section>
            <section className="side-panel">
              <h2>Format hóa đơn</h2>
              <p>Ảnh/PDF sample mới dùng mẫu hóa đơn bán hàng dạng giấy: tiêu đề cửa hàng, bảng 10 dòng hàng, cột số lượng, đơn giá, thành tiền và phần ký khách hàng/người bán.</p>
              <p>Sau khi generate, file được lưu trong database chung của backend. Nút xóa chỉ xóa sample generated, không xóa dữ liệu nghiệp vụ đã import.</p>
            </section>
          </section>
        )}

        {activeStep === "rules" && (
          <section className="step-layout">
            <form className="panel form-grid" onSubmit={saveRules}>
              <h2>1. Cấu hình rule trước khi chạy dữ liệu</h2>
              {[
                ["Auto-match threshold", "auto_match_threshold"],
                ["Manual-review threshold", "manual_review_threshold"],
                ["Date tolerance days", "date_tolerance_days"],
                ["Amount tolerance VND", "amount_tolerance_vnd"],
                ["Low OCR confidence threshold", "low_ocr_confidence_threshold"],
                ["VAT tolerance", "vat_tolerance"],
              ].map(([label, name]) => (
                <Field key={name} label={label} name={name} type="number" value={rules[name]} onChange={(event) => setRules({ ...rules, [name]: Number(event.target.value) })} />
              ))}
              <button type="submit" disabled={busy}>Lưu rule</button>
            </form>
            <section className="side-panel">
              <h2>Mục tiêu bước này</h2>
              <p>Rule được dùng cho validation, chọn candidate và phân loại match. Nên chốt rule trước khi import dữ liệu sample hoặc dữ liệu doanh nghiệp.</p>
              <Metric icon={Settings2} label="Auto threshold" value={rules.auto_match_threshold} />
              <Metric icon={AlertTriangle} label="Manual threshold" value={rules.manual_review_threshold} tone="warn" />
            </section>
          </section>
        )}

        {activeStep === "vendors" && (
          <section className="step-layout">
            <section className="panel">
              <h2>2. Import vendor master</h2>
              <div className="upload-grid single">
                <UploadCard
                  icon={FileSpreadsheet}
                  title="Vendor master CSV/XLSX"
                  helper="Nguồn kiểm tra vendor_id, tax_code, bank_account và trạng thái active/inactive."
                  inputRef={vendorFileRef}
                  accept=".csv,.xlsx,.xls"
                  onSubmit={() => importFile(vendorFileRef.current?.files?.[0], "/api/vendors/import", "vendor master")}
                  primary
                />
              </div>
              <DataTable
                rows={vendors.slice(0, 10)}
                columns={[
                  { key: "vendor_id", label: "Mã Mối buôn" },
                  { key: "vendor_name", label: "Tên mối buôn" },
                  { key: "tax_code", label: "Mã số thuế" },
                  { key: "bank_name", label: "Ngân hàng" },
                  { key: "bank_account", label: "Số tài khoản" },
                  { key: "bank_account_holder", label: "Chủ tài khoản" },
                  { key: "status", label: "Trạng thái", render: (row) => <StatusPill value={row.status} /> },
                ]}
              />
            </section>
            <section className="side-panel">
              <Metric icon={FileSpreadsheet} label="Vendor đã import" value={vendors.length} />
              <p>Đi tiếp khi vendor master đã có dữ liệu. Invoice register và payment batch sẽ dùng vendor master để kiểm soát trước thanh toán.</p>
            </section>
          </section>
        )}

        {activeStep === "invoice-source" && (
          <section className="panel">
            <h2>3. Tải lên phiếu nhập hàng / hóa đơn bán lẻ</h2>
            <p className="helper-text">
              Tải lên ảnh chụp phiếu giao hàng viết tay, biên nhận hoặc Excel. Tính năng OCR sẽ tự động đọc dữ liệu.
            </p>
            <div className="upload-grid">
              <UploadCard
                icon={Upload}
                title="Ảnh chụp phiếu viết tay (OCR)"
                helper="Tải lên ảnh/PDF phiếu nhập hàng viết tay để đọc tự động."
                inputRef={fallbackFilesRef}
                accept=".pdf,.png,.jpg,.jpeg,.txt,.xml"
                multiple
                onSubmit={() => uploadFallback(fallbackFilesRef.current?.files)}
                primary
              />
              <UploadCard
                icon={FileSpreadsheet}
                title="Bảng kê Excel/CSV"
                helper="File danh sách phiếu nhập chuẩn."
                inputRef={invoiceRegisterRef}
                accept=".csv,.xlsx,.xls"
                onSubmit={() => importFile(invoiceRegisterRef.current?.files?.[0], "/api/invoices/import-register", "invoice register")}
              />
            </div>
            <DataTable
              rows={invoices.slice(0, 12)}
              columns={[
                { key: "invoice_number", label: "Mã Phiếu" },
                { key: "vendor_name", label: "Mối buôn" },
                { key: "total_amount", label: "Tổng tiền", render: (row) => formatMoney(row.total_amount, row.currency) },
                { key: "ocr_confidence", label: "Độ tin cậy OCR", render: (row) => row.ocr_confidence !== null && row.ocr_confidence !== undefined ? `${row.ocr_confidence}%` : "-" },
                { key: "status", label: "Trạng thái", render: (row) => <StatusPill value={row.status} /> },
                {
                  key: "actions",
                  label: "Thao tác",
                  render: (row) => (
                    <button onClick={() => quickEditInvoice(row)} disabled={busy}>Sửa nhanh</button>
                  ),
                },
              ]}
            />
          </section>
        )}

        {activeStep === "prepayment" && (
          <section className="panel">
            <div className="section-head">
              <div>
                <h2>4. Kiểm tra phiếu nhập</h2>
                <p className="helper-text">Hệ thống sẽ chạy luật để phát hiện lỗi. Nếu ổn, hãy Duyệt phiếu để đưa vào danh sách trả tiền.</p>
              </div>
              <button onClick={runValidation} disabled={busy}>Chạy kiểm tra</button>
            </div>
            <div className="metrics-grid compact">
              <Metric icon={FileText} label="Tổng phiếu" value={invoices.length} />
              <Metric icon={CheckCircle2} label="Hợp lệ" value={invoices.filter((item) => item.status === "validated").length} tone="good" />
              <Metric icon={AlertTriangle} label="Có lỗi" value={reviewInvoices.length} tone="warn" />
              <Metric icon={Banknote} label="Đã duyệt" value={approvedInvoices.length} />
            </div>
            <DataTable
              rows={invoices}
              columns={[
                { key: "invoice_number", label: "Mã Phiếu" },
                { key: "vendor_name", label: "Mối buôn" },
                { key: "total_amount", label: "Tổng tiền", render: (row) => formatMoney(row.total_amount, row.currency) },
                { key: "validation_status", label: "Validation", render: (row) => <StatusPill value={row.validation_status} /> },
                { key: "status", label: "Trạng thái", render: (row) => <StatusPill value={row.status} /> },
                {
                  key: "actions",
                  label: "Thao tác",
                  render: (row) => (
                    <div className="row-actions">
                      <button onClick={() => approveInvoice(row)} disabled={busy}>Duyệt</button>
                      <button onClick={() => rejectInvoice(row)} disabled={busy}>Từ chối</button>
                    </div>
                  ),
                },
              ]}
            />
          </section>
        )}

        {activeStep === "payment" && (
          <section className="step-layout">
            <section className="panel">
              <div className="section-head">
                <div>
                  <h2>5. Bảng kê thanh toán</h2>
                  <p className="helper-text">Gom các phiếu đã duyệt vào bảng kê để biết cần trả bao nhiêu tiền cho mối nào.</p>
                </div>
                <button onClick={generatePaymentBatch} disabled={busy}>Sinh từ phiếu đã duyệt</button>
              </div>
              <div className="upload-grid single">
                <UploadCard
                  icon={ClipboardCheck}
                  title="Import bảng kê ngoài (Excel)"
                  helper="Nhập bảng kê thanh toán nếu có sẵn."
                  inputRef={paymentFileRef}
                  accept=".csv,.xlsx,.xls"
                  onSubmit={() => importFile(paymentFileRef.current?.files?.[0], "/api/payment-batches/import", "bảng kê")}
                  primary
                />
              </div>
              <DataTable
                rows={paymentBatches}
                columns={[
                  { key: "payment_id", label: "Mã Bảng kê" },
                  { key: "vendor_id", label: "Mối buôn" },
                  { key: "scheduled_payment_date", label: "Ngày trả" },
                  { key: "approved_amount", label: "Tiền cần trả", render: (row) => formatMoney(row.approved_amount, row.currency) },
                  { key: "approval_status", label: "Trạng thái", render: (row) => <StatusPill value={row.approval_status} /> },
                ]}
              />
            </section>
            <section className="side-panel">
              <Metric icon={ClipboardCheck} label="Dòng bảng kê" value={paymentBatches.length} />
              <Metric icon={CheckCircle2} label="Chờ trả" value={paymentBatches.filter((item) => item.approval_status === "approved").length} tone="good" />
            </section>
          </section>
        )}

        {activeStep === "bank" && (
          <section className="step-layout">
            <section className="panel">
              <h2>6. Import bank statement</h2>
              <div className="upload-grid single">
                <UploadCard
                  icon={Banknote}
                  title="Bank statement CSV/XLSX"
                  helper="Import sao kê sau khi có danh sách payment được duyệt."
                  inputRef={bankFileRef}
                  accept=".csv,.xlsx,.xls"
                  onSubmit={() => importFile(bankFileRef.current?.files?.[0], "/api/bank-transactions/import", "sao kê ngân hàng")}
                  primary
                />
              </div>
              <DataTable
                rows={transactions.slice(0, 20)}
                columns={[
                  { key: "transaction_id", label: "Mã GD" },
                  { key: "transaction_date", label: "Ngày" },
                  { key: "description", label: "Mô tả" },
                  { key: "amount", label: "Số tiền", render: (row) => formatMoney(row.amount, row.currency) },
                  { key: "direction", label: "Loại", render: (row) => <StatusPill value={row.direction} /> },
                  { key: "reference_code", label: "Reference" },
                ]}
              />
            </section>
            <section className="side-panel">
              <Metric icon={Banknote} label="Bank transactions" value={transactions.length} />
              <Metric icon={FileSpreadsheet} label="Outflow" value={transactions.filter((item) => item.direction === "outflow").length} />
            </section>
          </section>
        )}

        {activeStep === "reconcile" && (
          <section className="panel">
            <div className="section-head">
              <div>
                <h2>7. Đối soát payment với ngân hàng</h2>
                <p className="helper-text">Engine chỉ reconcile payment/invoice đã approved hoặc scheduled. Giao dịch ngân hàng không liên quan sẽ thành exception.</p>
              </div>
              <button onClick={runReconciliation} disabled={busy}>Chạy đối soát</button>
            </div>
            <div className="metrics-grid compact">
              <Metric icon={CheckCircle2} label="Matched/Reconciled" value={overview.matched_count || 0} tone="good" />
              <Metric icon={AlertTriangle} label="Amount mismatch" value={overview.amount_mismatch_count || 0} tone="danger" />
              <Metric icon={FileText} label="Approved unpaid" value={overview.unmatched_invoice_count || 0} tone="warn" />
              <Metric icon={Banknote} label="Unmatched bank" value={overview.unmatched_transaction_count || 0} tone="danger" />
            </div>
            <h2>Kết quả đối soát</h2>
            <DataTable
              rows={matches}
              columns={[
                { key: "vendor_name", label: "Mối buôn" },
                { key: "invoice_number", label: "Mã Phiếu" },
                { key: "invoice_amount", label: "Tiền Phiếu", render: (row) => formatMoney(row.invoice_amount) },
                { key: "transaction_description", label: "Nội dung CK" },
                { key: "transaction_amount", label: "Tiền CK", render: (row) => formatMoney(row.transaction_amount) },
                { key: "match_score", label: "Điểm số", render: (row) => `${row.match_score}/100` },
                { key: "match_status", label: "Trạng thái", render: (row) => <StatusPill value={row.match_status} /> },
                { key: "amount_diff", label: "Lệch tiền", render: (row) => formatMoney(row.amount_diff || 0) },
                { key: "reason", label: "Chi tiết đối soát" },
                {
                  key: "actions",
                  label: "Thao tác",
                  render: (row) => (
                    <div className="row-actions">
                      <button onClick={() => approveMatch(row.id)}>Duyệt</button>
                      <button onClick={() => rejectMatch(row.id)}>Từ chối</button>
                    </div>
                  ),
                },
              ]}
            />
            <h2>Ngoại lệ cần xử lý</h2>
            <DataTable
              rows={exceptions}
              columns={[
                { key: "exception_type", label: "Loại", render: (row) => <StatusPill value={row.exception_type} /> },
                { key: "severity", label: "Mức độ", render: (row) => <StatusPill value={row.severity} /> },
                { key: "status", label: "Trạng thái", render: (row) => <StatusPill value={row.status} /> },
                { key: "invoice_number", label: "Hóa đơn" },
                { key: "transaction_id", label: "Giao dịch" },
                { key: "message", label: "Nội dung" },
                {
                  key: "workflow",
                  label: "Xử lý",
                  render: (row) => (
                    <div className="exception-edit">
                      <select value={exceptionDrafts[row.id]?.status || row.status || "open"} onChange={(event) => setExceptionDrafts({ ...exceptionDrafts, [row.id]: { ...(exceptionDrafts[row.id] || {}), status: event.target.value } })}>
                        <option value="open">Mở</option>
                        <option value="in_review">Đang xử lý</option>
                        <option value="resolved">Đã xử lý</option>
                        <option value="dismissed">Bỏ qua</option>
                      </select>
                      <input placeholder="Ghi chú" value={exceptionDrafts[row.id]?.note || row.note || ""} onChange={(event) => setExceptionDrafts({ ...exceptionDrafts, [row.id]: { ...(exceptionDrafts[row.id] || {}), note: event.target.value } })} />
                      <button onClick={() => updateException(row.id, row.status)}>Lưu</button>
                    </div>
                  ),
                },
              ]}
            />
          </section>
        )}

        {activeStep === "dashboard" && (
          <section className="panel">
            <div className="section-head">
              <div>
                <h2>8. Dashboard quản lý và báo cáo</h2>
                <p className="helper-text">AI report chỉ diễn giải số liệu backend đã tính, không tự bịa số.</p>
              </div>
              <div className="row-actions">
                <button onClick={generateReport} disabled={busy}>Tạo báo cáo</button>
                <a className="button-link" href={`${API_BASE}/api/reports/export/reconciliation.xlsx`}>Export đối soát</a>
                <a className="button-link" href={`${API_BASE}/api/reports/export/exceptions.xlsx`}>Export ngoại lệ</a>
              </div>
            </div>
            <div className="metrics-grid">
              <Metric icon={FileText} label="Tổng hóa đơn" value={overview.total_invoices || 0} />
              <Metric icon={CheckCircle2} label="Tỷ lệ match" value={`${overview.match_rate || overview.matched_rate || 0}%`} tone="good" />
              <Metric icon={AlertTriangle} label="Ngoại lệ mở" value={overview.open_exceptions || 0} tone="warn" />
              <Metric icon={Banknote} label="Tổng tiền phiếu nhập" value={formatMoney(overview.total_invoice_value || 0)} />
              <Metric icon={Banknote} label="Tiền đã đối soát khớp" value={formatMoney(overview.matched_value || 0)} tone="good" />
              <Metric icon={Banknote} label="Giá trị chưa match" value={formatMoney(overview.unmatched_value || overview.total_unmatched_value || 0)} tone="danger" />
              <Metric icon={FileSpreadsheet} label="Giao dịch ngân hàng" value={overview.total_bank_transactions || 0} />
              <Metric icon={WandSparkles} label="OCR trung bình" value={`${overview.average_ocr_confidence || 0}%`} />
            </div>
            {reportText && <pre className="report-box">{reportText}</pre>}
            <div className="split">
              <section>
                <h2>Vendor có nhiều lỗi</h2>
                <DataTable
                  rows={overview.top_vendor_exceptions || []}
                  columns={[
                    { key: "vendor_name", label: "Vendor" },
                    { key: "count", label: "Số lỗi" },
                  ]}
                />
              </section>
              <section>
                <h2>Audit log gần đây</h2>
                <DataTable
                  rows={auditLogs.slice(0, 10)}
                  columns={[
                    { key: "action", label: "Hành động" },
                    { key: "entity_type", label: "Đối tượng" },
                    { key: "created_at", label: "Thời gian" },
                  ]}
                />
              </section>
            </div>
            <h2>Lịch sử báo cáo</h2>
            <DataTable
              rows={reports}
              columns={[
                { key: "report_type", label: "Loại" },
                { key: "report_content", label: "Nội dung" },
                { key: "created_at", label: "Tạo lúc" },
              ]}
            />
          </section>
        )}

        <footer className="step-footer">
          <button onClick={previousStep} disabled={activeIndex === 0}>Bước trước</button>
          <button onClick={nextStep} disabled={activeIndex === steps.length - 1}>Bước tiếp theo</button>
        </footer>
      </section>
    </main>
  );
}
