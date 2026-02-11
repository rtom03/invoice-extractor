import json
import os
import re
import timedelta
import requests
from datetime import datetime


SYSTEM_PROMPT = """You are an expert data extractor for sales invoices.
Extract structured fields and return ONLY valid JSON matching this schema:
{
  "document": {
    "VendorName": "",
    "InvoiceNumber": "",
    "InvoiceDate": "YYYY-MM-DD",
    "DueDate": "YYYY-MM-DD",
    "Terms": "",
    "BillToName": "",
    "BillToAddress": "",
    "ShipToName": "",
    "ShipToAddress": "",
    "Currency": "",
    "Notes": "",
    "Subtotal": 0,
    "Tax": 0,
    "Freight": 0,
    "Total": 0
  },
  "header": {
    "SalesOrderNumber": "",
    "OrderDate": "YYYY-MM-DD",
    "DueDate": "YYYY-MM-DD",
    "ShipDate": "YYYY-MM-DD",
    "PurchaseOrderNumber": "",
    "AccountNumber": "",
    "CustomerID": "",
    "SalesPersonID": "",
    "TerritoryID": "",
    "BillToAddressID": "",
    "ShipToAddressID": "",
    "ShipMethodID": "",
    "CreditCardID": "",
    "CreditCardApprovalCode": "",
    "CurrencyRateID": "",
    "SubTotal": 0,
    "TaxAmt": 0,
    "Freight": 0,
    "TotalDue": 0
  },
  "details": [
    {
      "OrderQty": 0,
      "ProductID": "",
      "ProductName": "",
      "UnitPrice": 0,
      "UnitPriceDiscount": 0,
      "LineTotal": 0,
      "CarrierTrackingNumber": "",
      "SpecialOfferID": ""
    }
  ]
}
Use null for any unknown value. Provide decimals as numbers, not strings.
"""


def extract_invoice(text=None, image_b64=None, mime_type=None):
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    # print(provider)
    if provider == "mock":
        return mock_extract(text or "")
    if provider == "openai_compatible":
        return openai_compatible_extract(text, image_b64, mime_type)
    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def openai_compatible_extract(text, image_b64, mime_type):
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1"
    model = os.getenv("LLM_MODEL") or "gpt-4o-mini"
    if not api_key:
        raise ValueError("LLM_API_KEY is required for openai_compatible provider")

    user_prompt = "Extract the invoice data from the document."
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if image_b64:
        content = [
            {"type": "text", "text": user_prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
            },
        ]
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": f"{user_prompt}\n\n{text}"})

    payload = {
        "model": model,
        "temperature": 0,
        "messages": messages,
    }

    if os.getenv("LLM_DISABLE_RESPONSE_FORMAT") not in ("1", "true", "TRUE"):
        payload["response_format"] = {"type": "json_object"}

    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=payload, timeout=90)
    if response.status_code >= 400 and "response_format" in payload:
        payload.pop("response_format", None)
        response = requests.post(url, headers=headers, json=payload, timeout=90)

    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]

    return parse_json_content(content)


def parse_json_content(content):
    if not content:
        return {}
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def normalize_extraction(data, raw_text=None, filename=None, mime_type=None):
    data = data or {}
    document = data.get("document") or {}
    header = data.get("header") or {}
    details = data.get("details") or []

    if raw_text and not document.get("RawText"):
        document["RawText"] = raw_text[:20000]
    if filename:
        document.setdefault("Filename", filename)
    if mime_type:
        document.setdefault("MimeType", mime_type)

    def safe_float(value):  # sanitize to float
        if value is None or value == "":
            return None
        if isinstance(value, (int, float)):
            return float(value)
        value = str(value).replace(",", "")
        value = re.sub(r"[^0-9.\-]", "", value)
        try:
            return float(value)
        except ValueError:
            return None

    def safe_int(value):  # sanitize to int
        if value is None or value == "":
            return None
        if isinstance(value, int):
            return value
        value = str(value).strip()
        value = re.sub(r"[^0-9\-]", "", value)
        try:
            return int(value)
        except ValueError:
            return None

    def parse_date(value):  # sanitize to date
        if not value:
            return None
        if isinstance(value, datetime):
            return value.date().isoformat()
        value = str(value).strip()
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%Y", "%b %d, %Y"):
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                continue
        return None

    def apply_terms(invoice_date, terms):
        if not invoice_date or not terms:
            return None
        match = re.search(r"net\s*(\d+)", terms, re.IGNORECASE)
        if not match:
            return None
        try:
            days = int(match.group(1))
        except ValueError:
            return None
        date_obj = datetime.strptime(invoice_date, "%Y-%m-%d")
        return (date_obj + timedelta(days=days)).date().isoformat()

    # Normalize document fields
    for key in ["Subtotal", "Tax", "Freight", "Total"]:
        document[key] = safe_float(document.get(key))

    if document.get("InvoiceDate"):
        document["InvoiceDate"] = parse_date(document.get("InvoiceDate"))
    if document.get("DueDate"):
        document["DueDate"] = parse_date(document.get("DueDate"))

    if not document.get("DueDate"):
        due_from_terms = apply_terms(document.get("InvoiceDate"), document.get("Terms"))
        if due_from_terms:
            document["DueDate"] = due_from_terms

    # Normalize header fields
    header["OrderDate"] = parse_date(
        header.get("OrderDate") or document.get("InvoiceDate"))
    header["DueDate"] = parse_date(header.get("DueDate") or document.get("DueDate"))
    header["ShipDate"] = parse_date(header.get("ShipDate"))
    header["SalesOrderNumber"] = header.get(
        "SalesOrderNumber") or document.get("InvoiceNumber")

    header["CustomerID"] = safe_int(header.get("CustomerID"))

    header["SubTotal"] = safe_float(header.get("SubTotal") or document.get("Subtotal"))
    header["TaxAmt"] = safe_float(header.get("TaxAmt") or document.get("Tax"))
    header["Freight"] = safe_float(header.get("Freight") or document.get("Freight"))
    header["TotalDue"] = safe_float(header.get("TotalDue") or document.get("Total"))

    if header.get("RevisionNumber") is None:
        header["RevisionNumber"] = 0
    if header.get("Status") is None:
        header["Status"] = 5
    if header.get("OnlineOrderFlag") is None:
        header["OnlineOrderFlag"] = 1

    normalized_details = []
    for item in details:
        item = item or {}
        item["OrderQty"] = safe_int(item.get("OrderQty"))
        item["UnitPrice"] = safe_float(item.get("UnitPrice"))
        item["UnitPriceDiscount"] = safe_float(item.get("UnitPriceDiscount")) or 0.0
        item["LineTotal"] = safe_float(item.get("LineTotal"))
        if item.get("LineTotal") is None and item.get(
                "OrderQty") and item.get("UnitPrice") is not None:
            item["LineTotal"] = item["OrderQty"] * item["UnitPrice"]
        normalized_details.append(item)

    details = normalized_details

    if header.get("SubTotal") is None:
        line_sum = sum([item.get("LineTotal") or 0 for item in details])
        header["SubTotal"] = line_sum if line_sum else None

    if header.get("TotalDue") is None:
        subtotal = header.get("SubTotal") or 0
        tax = header.get("TaxAmt") or 0
        freight = header.get("Freight") or 0
        total = subtotal + tax + freight
        header["TotalDue"] = total if total else None

    if document.get("Subtotal") is None:
        document["Subtotal"] = header.get("SubTotal")

    if document.get("Tax") is None:
        document["Tax"] = header.get("TaxAmt")

    if document.get("Freight") is None:
        document["Freight"] = header.get("Freight")

    if document.get("Total") is None:
        document["Total"] = header.get("TotalDue")
    return {"document": document, "header": header, "details": details}


def mock_extract(text):
    text = text or ""
    result = {
        "document": {},
        "header": {},
        "details": [],
    }

    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    result["document"]["InvoiceNumber"] = find(
        r"Invoice\s*(?:No|#|Number)[:\s]*([A-Za-z0-9-]+)")
    result["document"]["InvoiceDate"] = find(
        r"Invoice\s*Date[:\s]*([A-Za-z0-9/\-]+)") or find(r"Date\s*Issued[:\s]*([A-Za-z0-9/\-]+)")
    result["document"]["DueDate"] = find(
        r"Due\s*Date[:\s]*([A-Za-z0-9/\-]+)") or find(r"Due[:\s]*([A-Za-z0-9/\-]+)")
    result["document"]["Terms"] = find(r"Terms[:\s]*([A-Za-z0-9\s-]+)")
    result["document"]["VendorName"] = find(
        r"^([A-Za-z0-9 &.,-]+)\n(?:Invoice|INVOICE)")
    result["document"]["BillToName"] = find(r"Bill To[:\s]*([A-Za-z0-9 &.,-]+)")
    result["document"]["ShipToName"] = find(r"Ship To[:\s]*([A-Za-z0-9 &.,-]+)")
    result["document"]["BillToAddress"] = find(r"Bill To(?:.*)\n([A-Za-z0-9 ,.-]+)")
    result["document"]["ShipToAddress"] = find(r"Ship To(?:.*)\n([A-Za-z0-9 ,.-]+)")
    result["document"]["Subtotal"] = find(r"Subtotal[:\s]*\$?([0-9,\.]+)")
    result["document"]["Tax"] = find(r"Tax[:\s]*\$?([0-9,\.]+)")
    result["document"]["Freight"] = find(r"Freight[:\s]*\$?([0-9,\.]+)")
    result["document"]["Total"] = find(r"Total[:\s]*\$?([0-9,\.]+)")

    result["header"]["SalesOrderNumber"] = find(
        r"Sales\s*Order[:\s]*([A-Za-z0-9-]+)") or result["document"].get("InvoiceNumber")
    result["header"]["PurchaseOrderNumber"] = find(
        r"PO\s*(?:Number)?:\s*([A-Za-z0-9-]+)")
    result["header"]["AccountNumber"] = find(r"Account\s*Number[:\s]*([A-Za-z0-9-]+)")
    result["header"]["CustomerID"] = find(r"Customer\s*ID[:\s]*([A-Za-z0-9-]+)")

    line_items = []
    for line in text.splitlines():
        line = line.strip()
        if not line or "Qty" in line and "Unit" in line:
            continue
        pattern = r"SKU\s*([A-Za-z0-9-]+)\s*-\s*([^\-]+)\s*-\s*Qty\s*(\d+)\s*-\s*Unit\s*\$?([0-9.]+)\s*-\s*Line\s*\$?([0-9.]+)"
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            line_items.append(
                {
                    "ProductID": match.group(1),
                    "ProductName": match.group(2).strip(),
                    "OrderQty": match.group(3),
                    "UnitPrice": match.group(4),
                    "LineTotal": match.group(5),
                }
            )
            continue
        table_pattern = r"(\d+)\s*\|\s*([A-Za-z0-9-]+)\s*\|\s*([^|]+)\|\s*([0-9.]+)\s*\|\s*([0-9.]+)"
        match = re.search(table_pattern, line)
        if match:
            line_items.append(
                {
                    "OrderQty": match.group(1),
                    "ProductID": match.group(2),
                    "ProductName": match.group(3).strip(),
                    "UnitPrice": match.group(4),
                    "LineTotal": match.group(5),
                }
            )
    result["details"] = line_items
    return result
