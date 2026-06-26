from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = BACKEND_DIR / "data"
DEFAULT_UPLOAD_DIR = DEFAULT_DATA_DIR / "uploads"

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", DEFAULT_DATA_DIR / "finrecon.db"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", DEFAULT_UPLOAD_DIR))


def ensure_storage() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    ensure_storage()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT,
                file_category TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS processing_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                job_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                started_at TEXT,
                finished_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(file_id) REFERENCES uploaded_files(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id TEXT,
                vendor_name TEXT NOT NULL,
                tax_code TEXT,
                bank_account TEXT,
                address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT,
                vendor_name TEXT,
                vendor_tax_code TEXT,
                invoice_date TEXT,
                due_date TEXT,
                subtotal REAL,
                vat_amount REAL,
                total_amount REAL,
                currency TEXT DEFAULT 'VND',
                status TEXT DEFAULT 'needs_review',
                validation_status TEXT DEFAULT 'pending',
                ocr_confidence REAL,
                uploaded_file_id INTEGER,
                processing_job_id INTEGER,
                source_file_name TEXT,
                source_file_path TEXT,
                raw_text TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(uploaded_file_id) REFERENCES uploaded_files(id) ON DELETE SET NULL,
                FOREIGN KEY(processing_job_id) REFERENCES processing_jobs(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS bank_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT,
                transaction_date TEXT,
                description TEXT,
                amount REAL NOT NULL,
                direction TEXT,
                bank_account TEXT,
                reference_code TEXT,
                validation_status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reconciliation_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                bank_transaction_id INTEGER,
                match_score REAL,
                match_status TEXT,
                amount_diff REAL,
                date_diff INTEGER,
                reason TEXT,
                approved INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                FOREIGN KEY(bank_transaction_id) REFERENCES bank_transactions(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS reconciliation_exceptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                bank_transaction_id INTEGER,
                exception_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                resolved INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                FOREIGN KEY(bank_transaction_id) REFERENCES bank_transactions(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ai_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT,
                report_content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        _ensure_column(conn, "invoices", "uploaded_file_id", "INTEGER")
        _ensure_column(conn, "invoices", "processing_job_id", "INTEGER")
        _ensure_column(conn, "bank_transactions", "validation_status", "TEXT DEFAULT 'pending'")


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]
