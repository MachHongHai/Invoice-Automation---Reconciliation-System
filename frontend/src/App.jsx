import { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  Banknote,
  CheckCircle2,
  FileSpreadsheet,
  FileText,
  RefreshCw,
  Upload,
  WandSparkles,
  XCircle,
} from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const emptyInvoice = {
  invoice_number: "",
  vendor_name: "",
  vendor_tax_code: "",
  invoice_date: "",
  due_date: "",
  subtotal: "",
  vat_amount: "",
  total_amount: "",
  currency: "VND",
  ocr_confidence: "",
};

const tabs = [
  { id: "invoices", label: "Invoices" },
  { id: "transactions", label: "Bank Transactions" },
  { id: "matches", label: "Matches" },
  { id: "exceptions", label: "Exceptions" },
  { id: "report", label: "Report" },
];

function formatMoney(value, currency = "VND") {
  if (value === null || value === undefined || value === "") return "-";
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(Number(value)) + ` ${currency}`;
}

function StatusPill({ value }) {
  const normalized = String(value || "pending").toLowerCase();
  return <span className={`pill ${normalized.replaceAll("_", "-")}`}>{value || "pending"}</span>;
}

function Metric({ icon: Icon, label, value, tone }) {
  return (
    <section className={`metric ${tone || ""}`}>
      <div className="metric-icon">
        <Icon size={18} aria-hidden="true" />
      </div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </section>
  );
}

function DataTable({ columns, rows, empty }) {
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
            rows.map((row) => (
              <tr key={row.id}>
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

export default function App() {
  const [activeTab, setActiveTab] = useState("invoices");
  const [overview, setOverview] = useState({});
  const [vendors, setVendors] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [matches, setMatches] = useState([]);
  const [exceptions, setExceptions] = useState([]);
  const [report, setReport] = useState("");
  const [invoiceForm, setInvoiceForm] = useState(emptyInvoice);
  const [invoiceFile, setInvoiceFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");

  const vendorFileRef = useRef(null);
  const bankFileRef = useRef(null);

  async function request(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, options);
    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || `Request failed: ${response.status}`);
    }
    return response.json();
  }

  async function refresh() {
    const [nextOverview, nextVendors, nextInvoices, nextTransactions, nextMatches, nextExceptions] =
      await Promise.all([
        request("/api/dashboard/overview"),
        request("/api/vendors"),
        request("/api/invoices"),
        request("/api/bank-transactions"),
        request("/api/reconciliation/results"),
        request("/api/reconciliation/exceptions"),
      ]);
    setOverview(nextOverview);
    setVendors(nextVendors);
    setInvoices(nextInvoices);
    setTransactions(nextTransactions);
    setMatches(nextMatches);
    setExceptions(nextExceptions);
  }

  useEffect(() => {
    refresh().catch((error) => setNotice(error.message));
  }, []);

  async function withBusy(action, successMessage) {
    setBusy(true);
    setNotice("");
    try {
      await action();
      await refresh();
      setNotice(successMessage);
    } catch (error) {
      setNotice(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function importCsv(file, endpoint, label) {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    await withBusy(
      () => request(endpoint, { method: "POST", body: form }),
      `${label} imported`,
    );
  }

  async function submitInvoice(event) {
    event.preventDefault();
    await withBusy(async () => {
      if (invoiceFile) {
        const form = new FormData();
        form.append("file", invoiceFile);
        Object.entries(invoiceForm).forEach(([key, value]) => {
          if (value !== "") form.append(key, value);
        });
        await request("/api/invoices/upload", { method: "POST", body: form });
      } else {
        await request("/api/invoices/manual", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(
            Object.fromEntries(Object.entries(invoiceForm).map(([key, value]) => [key, value || null])),
          ),
        });
      }
      setInvoiceForm(emptyInvoice);
      setInvoiceFile(null);
    }, "Invoice saved");
  }

  async function runReconciliation() {
    await withBusy(
      () => request("/api/reconciliation/run", { method: "POST" }),
      "Reconciliation completed",
    );
  }

  async function generateReport() {
    await withBusy(async () => {
      const data = await request("/api/reports/daily");
      setReport(data.report);
      setActiveTab("report");
    }, "Report generated");
  }

  const invoiceColumns = useMemo(
    () => [
      { key: "invoice_number", label: "Invoice" },
      { key: "vendor_name", label: "Vendor" },
      { key: "invoice_date", label: "Date" },
      { key: "total_amount", label: "Total", render: (row) => formatMoney(row.total_amount, row.currency) },
      { key: "validation_status", label: "Validation", render: (row) => <StatusPill value={row.validation_status} /> },
      { key: "status", label: "Status", render: (row) => <StatusPill value={row.status} /> },
    ],
    [],
  );

  const transactionColumns = useMemo(
    () => [
      { key: "transaction_id", label: "Transaction" },
      { key: "transaction_date", label: "Date" },
      { key: "description", label: "Description" },
      { key: "amount", label: "Amount", render: (row) => formatMoney(row.amount) },
      { key: "direction", label: "Direction", render: (row) => <StatusPill value={row.direction} /> },
    ],
    [],
  );

  const matchColumns = useMemo(
    () => [
      { key: "invoice_number", label: "Invoice" },
      { key: "transaction_id", label: "Transaction" },
      { key: "match_score", label: "Score", render: (row) => Number(row.match_score || 0).toFixed(2) },
      { key: "match_status", label: "Status", render: (row) => <StatusPill value={row.match_status} /> },
      { key: "amount_diff", label: "Amount Diff", render: (row) => formatMoney(row.amount_diff) },
      { key: "reason", label: "Reason" },
    ],
    [],
  );

  const exceptionColumns = useMemo(
    () => [
      { key: "exception_type", label: "Type", render: (row) => <StatusPill value={row.exception_type} /> },
      { key: "severity", label: "Severity", render: (row) => <StatusPill value={row.severity} /> },
      { key: "invoice_number", label: "Invoice" },
      { key: "transaction_id", label: "Transaction" },
      { key: "message", label: "Message" },
    ],
    [],
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Finance operations</p>
          <h1>FinRecon AI</h1>
        </div>
        <div className="topbar-actions">
          <button title="Refresh data" onClick={() => withBusy(refresh, "Data refreshed")} disabled={busy}>
            <RefreshCw size={17} aria-hidden="true" />
            Refresh
          </button>
          <button className="primary" title="Run reconciliation" onClick={runReconciliation} disabled={busy}>
            <WandSparkles size={17} aria-hidden="true" />
            Reconcile
          </button>
        </div>
      </header>

      <section className="metrics-grid">
        <Metric icon={FileText} label="Invoices" value={overview.total_invoices || 0} />
        <Metric icon={CheckCircle2} label="Matched Rate" value={`${overview.matched_rate || 0}%`} tone="green" />
        <Metric icon={AlertTriangle} label="Open Exceptions" value={overview.open_exceptions || 0} tone="amber" />
        <Metric icon={XCircle} label="Unmatched Value" value={formatMoney(overview.total_unmatched_value || 0)} tone="red" />
      </section>

      <div className="workspace">
        <aside className="operations-panel">
          <section className="panel">
            <div className="panel-heading">
              <FileSpreadsheet size={18} aria-hidden="true" />
              <h2>Imports</h2>
            </div>
            <input
              ref={vendorFileRef}
              className="hidden-input"
              type="file"
              accept=".csv"
              onChange={(event) => importCsv(event.target.files?.[0], "/api/vendors/import", "Vendors")}
            />
            <input
              ref={bankFileRef}
              className="hidden-input"
              type="file"
              accept=".csv"
              onChange={(event) => importCsv(event.target.files?.[0], "/api/bank-transactions/import", "Transactions")}
            />
            <button title="Import vendor master CSV" onClick={() => vendorFileRef.current?.click()} disabled={busy}>
              <Upload size={17} aria-hidden="true" />
              Vendor CSV
            </button>
            <button title="Import bank statement CSV" onClick={() => bankFileRef.current?.click()} disabled={busy}>
              <Banknote size={17} aria-hidden="true" />
              Bank CSV
            </button>
            <div className="import-counts">
              <span>{vendors.length} vendors</span>
              <span>{transactions.length} transactions</span>
            </div>
          </section>

          <form className="panel invoice-form" onSubmit={submitInvoice}>
            <div className="panel-heading">
              <FileText size={18} aria-hidden="true" />
              <h2>Invoice Intake</h2>
            </div>
            <label>
              File
              <input type="file" onChange={(event) => setInvoiceFile(event.target.files?.[0] || null)} />
            </label>
            <label>
              Invoice number
              <input
                value={invoiceForm.invoice_number}
                onChange={(event) => setInvoiceForm({ ...invoiceForm, invoice_number: event.target.value })}
              />
            </label>
            <label>
              Vendor
              <input
                value={invoiceForm.vendor_name}
                onChange={(event) => setInvoiceForm({ ...invoiceForm, vendor_name: event.target.value })}
              />
            </label>
            <label>
              Invoice date
              <input
                type="date"
                value={invoiceForm.invoice_date}
                onChange={(event) => setInvoiceForm({ ...invoiceForm, invoice_date: event.target.value })}
              />
            </label>
            <div className="form-grid">
              <label>
                Subtotal
                <input
                  inputMode="decimal"
                  value={invoiceForm.subtotal}
                  onChange={(event) => setInvoiceForm({ ...invoiceForm, subtotal: event.target.value })}
                />
              </label>
              <label>
                VAT
                <input
                  inputMode="decimal"
                  value={invoiceForm.vat_amount}
                  onChange={(event) => setInvoiceForm({ ...invoiceForm, vat_amount: event.target.value })}
                />
              </label>
            </div>
            <label>
              Total
              <input
                inputMode="decimal"
                value={invoiceForm.total_amount}
                onChange={(event) => setInvoiceForm({ ...invoiceForm, total_amount: event.target.value })}
              />
            </label>
            <button className="primary full" title="Save invoice" type="submit" disabled={busy}>
              <Upload size={17} aria-hidden="true" />
              Save Invoice
            </button>
          </form>
        </aside>

        <section className="workbench">
          <div className="tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={activeTab === tab.id ? "active" : ""}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {notice ? <div className="notice">{notice}</div> : null}

          {activeTab === "invoices" && (
            <DataTable columns={invoiceColumns} rows={invoices} empty="No invoices yet." />
          )}
          {activeTab === "transactions" && (
            <DataTable columns={transactionColumns} rows={transactions} empty="No bank transactions yet." />
          )}
          {activeTab === "matches" && (
            <DataTable columns={matchColumns} rows={matches} empty="No reconciliation results yet." />
          )}
          {activeTab === "exceptions" && (
            <DataTable columns={exceptionColumns} rows={exceptions} empty="No exceptions yet." />
          )}
          {activeTab === "report" && (
            <section className="report-panel">
              <div className="report-actions">
                <h2>AI Report</h2>
                <button title="Generate report" onClick={generateReport} disabled={busy}>
                  <WandSparkles size={17} aria-hidden="true" />
                  Generate
                </button>
              </div>
              <pre>{report || "No report generated."}</pre>
            </section>
          )}
        </section>
      </div>
    </main>
  );
}

