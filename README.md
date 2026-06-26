# FinRecon AI

Invoice automation and bank reconciliation web app with a FastAPI backend and React frontend.

## What is included

- Vendor master CSV import
- Bank statement CSV import
- Invoice upload with optional manual extraction fields
- Manual invoice creation
- Invoice validation rules
- Rule-based reconciliation scoring
- Exception classification
- Dashboard metrics
- AI-style reconciliation report generated from computed results
- Docker Compose for local development

## Run locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
npm run dev
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: http://127.0.0.1:5173
- Backend API docs: http://127.0.0.1:8000/docs

## Run with Docker

```bash
docker compose up --build
```

## CSV formats

Vendor master columns:

```csv
vendor_id,vendor_name,tax_code,bank_account,address
```

Bank statement columns:

```csv
transaction_id,transaction_date,description,amount,direction,bank_account
```

Dates should use `YYYY-MM-DD` or `DD/MM/YYYY`. Amounts can include separators such as `6,050,000`.

## Reconciliation scoring

The backend computes match candidates with:

- 45% amount similarity
- 25% date proximity
- 20% vendor similarity
- 10% invoice number or reference similarity

The report endpoint only explains backend-computed results. It does not calculate financial totals with an LLM.
