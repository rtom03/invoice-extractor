Project: backend (stryker-test)
Generated: 2026-02-09T16:30:37Z

## Purpose

This document explains the Python backend application files found in the backend/ directory. It walks through the entrypoint (app.py), database module (db.py), language-model extraction logic (llm.py), route blueprints (routes/), and the supporting import script. Each function and important variable is explained with its role and essential details.

## Files overview

- app.py: Flask application entrypoint and factory.
- db.py: SQLite database schema, helpers, and CRUD for orders/documents/details.
- llm.py: Invoice extraction logic; supports a mock extractor and an "openai_compatible" provider; parsing and normalization utilities.
- routes/**init**.py: package marker.
- routes/health.py: simple health-check endpoint.
- routes/extract.py: file upload + extraction endpoint; converts files, calls llm.extract_invoice and returns normalized extraction.
- routes/orders.py: endpoints for listing, creating, updating and snapshotting orders.
- scripts/import_excel.py: utility to import SalesOrderHeader/SalesOrderDetail from data.xlsx into the DB.
- requirements.txt: third-party Python package dependencies.

## Detailed file-by-file explanation

1. app.py

---

Key parts:

- create_app(): constructs Flask app, registers CORS, registers three blueprints (health, orders, extract), calls init_db() to ensure DB schema exists. seed_db() is present but commented out.
- app = create_app() and the module-level **main** block runs the Flask development server on PORT env or 5000 with debug=True.

Essence: app.py is the application factory and startup script. By encapsulating creation in create_app it supports import-based use in testing or WSGI servers.

2. db.py
   --- Top-level constants:

- DB_PATH: path to SQLite file (env DATABASE_PATH or backend/data/app.db).
- HEADER_COLUMNS, DETAIL_COLUMNS, DOCUMENT_COLUMNS: canonical column lists used for constructing INSERT/UPDATE payloads consistently across scripts.
- SCHEMA_SQL: SQL used to create three tables: Documents, SalesOrderHeader, SalesOrderDetail and an index for SalesOrderDetail.

Key functions:

- get_conn(): returns sqlite3.Connection with row_factory = sqlite3.Row so rows can be accessed by column name.
- init_db(): ensures containing directory exists and runs SCHEMA_SQL via conn.executescript to create tables if missing.
- \_row_to_dict(row): converts sqlite3.Row or None to a plain dict (or None). Used before JSONifying results.
- next_sales_order_id(conn): determines next SalesOrderID by taking MAX(SalesOrderID) from SalesOrderHeader; defaults to 50000 if none found, then returns max+1.
- seed_db(): inserts a small set of example headers, details and documents if SalesOrderHeader is empty. Uses datetime.utcnow() for CreatedAt on documents. This is a convenience for development/testing.

CRUD and helper APIs:

- fetch_orders(limit=25): returns last N SalesOrderHeader rows joined with Documents (left join) ordered by SalesOrderID desc. Returns list of dicts.
- fetch_order(order_id): fetches header, document and all details for a specific SalesOrderID and returns a dict {header, document, details} where each sub-item is converted via \_row_to_dict.
- insert_order(payload): accepts a payload with keys: header, document, details. Ensures a SalesOrderID is present (uses next_sales_order_id when missing), inserts header, optionally inserts document (with CreatedAt timestamp), inserts all details. Then returns fetch_order(sales_order_id).
  - Uses HEADER_COLUMNS/DETAIL_COLUMNS/DOCUMENT_COLUMNS to enforce column ordering and to avoid unexpected columns.
- update_order(order_id, payload): updates SalesOrderHeader row (sets columns except SalesOrderID), upserts Documents (updates if existing document for that SalesOrderID, otherwise inserts with CreatedAt), deletes existing SalesOrderDetail rows for that SalesOrderID then reinserts provided details. Returns fetch_order(order_id).
- db_snapshot(limit=10): returns recent N rows for headers, details and documents (each list) for quick inspection.

Essence: db.py centralizes schema and atomic DB operations with defensive use of canonical column lists, safe connections, and simple upsert/update semantics.

3. llm.py

---

Purpose: Provide document-to-structured-data extraction for invoices. Offers:

- A mock rule-based extractor (mock_extract) for local testing.
- An "openai_compatible" provider to call a generative model via HTTP POST (compatible with OpenAI-like chat completions) when environment variables are properly set.
- Common parsing and normalization utilities to coerce data types, parse dates, and compute missing fields.

Key elements:

- SYSTEM_PROMPT: instructs the model to return a specific JSON schema (document, header, details). This prompt is used when calling the LLM provider.
- extract_invoice(text=None, image_b64=None, mime_type=None): chooses provider based on LLM_PROVIDER env var; default is "mock".
- openai_compatible_extract(...): constructs messages with system prompt and either text or an image payload, sets model and response_format (json_object) unless disabled, posts to LLM_BASE_URL/chat/completions with LLM_API_KEY in Authorization header, handles a fallback if the response_format causes a 4xx error, parses the returned content using parse_json_content.
- parse_json_content(content): attempts a direct JSON loads, and if fails, extracts the first {...} substring via regex then json.loads it. This makes the integration resilient to models that add commentary outside raw JSON.

Normalization helpers:

- normalize_extraction(data, raw_text=None, filename=None, mime_type=None): the main function used by routes to coerce extracted data into DB-ready types and fill sensible defaults. Important internal helpers:
  - safe_float(value): strips currency characters, commas and returns float or None.
  - safe_int(value): strips non-numeric chars and returns int or None.
  - parse_date(value): attempts several common formats and returns ISO date string or None.
  - apply_terms(invoice_date, terms): if terms like "Net 30" exists, computes DueDate by adding days to invoice_date.

Normalization steps:

- Normalizes document numeric fields (Subtotal, Tax, Freight, Total) and dates.
- Derives header dates from document dates when missing; sets default RevisionNumber=0, Status=5, OnlineOrderFlag=1 if not provided.
- Normalizes each detail row (OrderQty int, UnitPrice float, UnitPriceDiscount default 0.0, computes LineTotal when missing).
- Computes header.SubTotal as sum of line totals when missing; computes TotalDue as subtotal + tax + freight when missing. Copies back numeric totals into document if missing.

- mock_extract(text): a heuristic, regex-driven extraction that finds invoice number, dates, vendor name, addresses, simple subtotal/tax/total patterns, and attempts to parse line items from free text lines using a couple of regex patterns. Useful for local dev without an LLM.

Essence: llm.py provides both model integration and robust sanitization/normalization to ensure downstream DB inserts are consistent and typed.

4. routes/health.py

---

- Exposes GET /api/health returning JSON {"status": "ok"}.

Essence: simple readiness/liveness endpoint used by monitoring or smoke tests.

5. routes/extract.py

---

Key parts:

- UPLOAD_DIR env-controlled path for saving uploaded files (default backend/../data/uploads).
- extract_text_from_pdf(data): uses pypdf.PdfReader to extract textual content page-by-page; returns combined text or None if pypdf not available or extraction fails.
- load_text_from_file(data, filename, mime_type): decides how to get text from uploaded bytes: decodes common text types and .txt/.md/.csv; if PDF file, calls extract_text_from_pdf. Otherwise returns None.
- /api/extract (POST): main flow:
  1. Requires file in request.files["file"].
  2. Secures filename and saves it under UPLOAD_DIR.
  3. Determines mime type and tries to obtain text or base64-encoded image (image types are base64-encoded and passed to LLM as an image payload).
  4. If neither text nor image content found, returns 400 error.
  5. Calls extract_invoice(text=image_b64/mime_type) to get extraction result, then normalize_extraction to coerce values and add a meta.processing_ms metric.
  6. Returns JSON normalized extraction.

Essence: Handles file upload, basic text extraction and coordinates the LLM extraction and normalization.

6. routes/orders.py

---

- GET /api/orders: returns fetch_orders(limit) where limit comes from query param.
- POST /api/orders: accepts JSON payload, runs normalize_extraction on it, then insert_order and returns created order 201.
- GET /api/orders/<order_id>: returns full order with header, document, details.
- PUT /api/orders/<order_id>: accepts JSON payload, normalize_extraction, update_order and returns updated order.
- GET /api/db_snapshot: convenience endpoint returning recent rows for debugging/inspection.

Essence: Standard RESTful-ish endpoints backed by db.py; normalization is applied to inbound payloads so the DB layer receives typed/sane values.

7. scripts/import_excel.py

---

Purpose: import SalesOrderHeader and SalesOrderDetail from an Excel file (data.xlsx in repo root) into the SQLite DB.
Key behavior:

- Uses openpyxl to read two sheets SalesOrderHeader and SalesOrderDetail (if present).
- maybe_date: tries to normalize Excel numeric dates or Python datetimes to ISO date strings.
- load_sheet: reads worksheet rows into list-of-dicts keyed by header row.
- main(): validates file exists, calls init_db(), reads sheets, optionally resets DB when invoked with --reset, and inserts rows with INSERT OR IGNORE for headers and simple INSERT for details.

Essence: A pragmatic one-off importer for seeding DB from spreadsheets.

## requirements.txt

Primary dependencies include Flask, flask-cors, requests, pypdf, openpyxl, python-dotenv. These support the web server, CORS, LLM HTTP calls, PDF parsing, Excel import and environment vars.

## Operational notes and important behaviors

- Database concurrency and transactions: functions use sqlite3 connections in context managers. Commits happen automatically on context exit. For more concurrent usage consider WAL mode or a different DB in production.
- Data validation: normalize_extraction performs conversion and best-effort parsing but it does not enforce schema-level validations beyond types and computed totals. Caller code is expected to rely on this normalization before DB writes.
- LLM provider: set LLM_PROVIDER to "openai_compatible" and provide LLM_API_KEY and optionally LLM_BASE_URL/LLM_MODEL. Otherwise mock provider is used.
- Security: uploaded files are saved and not currently scanned or size-limited; consider limits and cleanup for production.
- Error handling: endpoints return 400 for clearly invalid requests; internal exceptions will propagate to Flask default error handlers in debug mode. Consider adding structured error handling for production.

## Appendix: quick function map (high level)

- app.create_app(): build Flask app and register blueprints
- db.init_db(), db.seed_db(), db.fetch_orders(), db.fetch_order(), db.insert_order(), db.update_order(), db.db_snapshot()
- llm.extract_invoice(), llm.openai_compatible_extract(), llm.parse_json_content(), llm.normalize_extraction(), llm.mock_extract()
- routes.extract.extract(), routes.extract.extract_text_from_pdf(), routes.extract.load_text_from_file()
- routes.orders.orders(), routes.orders.order_detail(), routes.orders.snapshot()

End of analysis.
