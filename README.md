# Document Extraction Demo (React/Next.js + Flask)

Atlas Extract is a demo app that uploads invoices, extracts structured fields with an LLM, and stores results in a SQLite database that mirrors **SalesOrderHeader** and **SalesOrderDetail**.

## Architecture

- **Frontend**: Next.js (React) UI with upload + editable extraction view.
- **Backend**: Flask API for file ingestion, LLM extraction, and SQLite persistence.
- **Database**: SQLite tables for `SalesOrderHeader`, `SalesOrderDetail`, plus a `Documents` table for invoice metadata.

## Setup

### Backend

```
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
```

Create an env file:

```
copy .env.example .env
```

Update LLM values in `.env`:

- `LLM_API_KEY=...`
- Optional: `LLM_BASE_URL` (defaults to https://api.openai.com/v1)
- Optional: `LLM_MODEL` (defaults to gpt-4o-mini)
- `LLM_PROVIDER=openai_compatible`

For offline demos, set `LLM_PROVIDER=mock`.

Run the API:

```
python app.py
```

1

### Frontend

```
cd frontend
npm install
```

Create an env file:

```
copy .env.example .env.local
```

Run the UI:

```
npm run dev
```

Open http://localhost:3000

## Demo Flow

1. Start backend and frontend.
2. Upload a sample invoice from `sample_invoices/` or the provided `Sales Invoice.png`.
3. Inspect extracted metadata + line items, edit if needed.
4. Click **Save to Database** and watch the **Database Snapshot** update.

## Using data.xlsx

If you want to preload the SQLite database with SalesOrderHeader/Detail rows from `data.xlsx`:

```
cd backend
python scripts/import_excel.py --reset
```

## Scaling Strategies (talking points)

- **Throughput**: Move extraction to a worker queue (Celery/RQ) with autoscaling workers; return job IDs and stream results to the UI.
- **Latency**: Cache repeated vendors/templates; store OCR text to avoid reprocessing.
- **Document Types**: Use a routing layer to detect document type and apply tailored prompts or fine-tuned models.
- **Reliability**: Add validation rules + confidence scores; surface low-confidence fields for human review.
- **Production**: Containerize services, add Postgres, use object storage for originals, and add observability (metrics + tracing).

## Notes

- `Documents` stores invoice metadata (bill/ship to, terms, totals). `SalesOrderHeader` + `SalesOrderDetail` mirror the Excel schema.
- `sample_invoices/` files are shaped to resemble SalesOrderHeader/Detail values for easy comparison.
