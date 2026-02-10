import os
import sqlite3
from datetime import datetime

DB_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "data", "app.db"),
)

HEADER_COLUMNS = [
    "SalesOrderID",
    "RevisionNumber",
    "OrderDate",
    "DueDate",
    "ShipDate",
    "Status",
    "OnlineOrderFlag",
    "SalesOrderNumber",
    "PurchaseOrderNumber",
    "AccountNumber",
    "CustomerID",
    "SalesPersonID",
    "TerritoryID",
    "BillToAddressID",
    "ShipToAddressID",
    "ShipMethodID",
    "CreditCardID",
    "CreditCardApprovalCode",
    "CurrencyRateID",
    "SubTotal",
    "TaxAmt",
    "Freight",
    "TotalDue",
]

DETAIL_COLUMNS = [
    "SalesOrderDetailID",
    "SalesOrderID",
    "CarrierTrackingNumber",
    "OrderQty",
    "ProductID",
    "ProductName",
    "SpecialOfferID",
    "UnitPrice",
    "UnitPriceDiscount",
    "LineTotal",
]

DOCUMENT_COLUMNS = [
    "DocumentID",
    "SalesOrderID",
    "Filename",
    "MimeType",
    "VendorName",
    "InvoiceNumber",
    "InvoiceDate",
    "DueDate",
    "Terms",
    "BillToName",
    "BillToAddress",
    "ShipToName",
    "ShipToAddress",
    "Currency",
    "Notes",
    "Subtotal",
    "Tax",
    "Freight",
    "Total",
    "RawText",
    "CreatedAt",
]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS Documents (
    DocumentID INTEGER PRIMARY KEY AUTOINCREMENT,
    SalesOrderID INTEGER,
    Filename TEXT,
    MimeType TEXT,
    VendorName TEXT,
    InvoiceNumber TEXT,
    InvoiceDate TEXT,
    DueDate TEXT,
    Terms TEXT,
    BillToName TEXT,
    BillToAddress TEXT,
    ShipToName TEXT,
    ShipToAddress TEXT,
    Currency TEXT,
    Notes TEXT,
    Subtotal REAL,
    Tax REAL,
    Freight REAL,
    Total REAL,
    RawText TEXT,
    CreatedAt TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS SalesOrderHeader (
    SalesOrderID INTEGER PRIMARY KEY,
    RevisionNumber INTEGER,
    OrderDate TEXT,
    DueDate TEXT,
    ShipDate TEXT,
    Status INTEGER,
    OnlineOrderFlag INTEGER,
    SalesOrderNumber TEXT,
    PurchaseOrderNumber TEXT,
    AccountNumber TEXT,
    CustomerID INTEGER,
    SalesPersonID INTEGER,
    TerritoryID INTEGER,
    BillToAddressID INTEGER,
    ShipToAddressID INTEGER,
    ShipMethodID INTEGER,
    CreditCardID INTEGER,
    CreditCardApprovalCode TEXT,
    CurrencyRateID INTEGER,
    SubTotal REAL,
    TaxAmt REAL,
    Freight REAL,
    TotalDue REAL
);

CREATE TABLE IF NOT EXISTS SalesOrderDetail (
    SalesOrderDetailID INTEGER PRIMARY KEY AUTOINCREMENT,
    SalesOrderID INTEGER,
    CarrierTrackingNumber TEXT,
    OrderQty INTEGER,
    ProductID TEXT,
    ProductName TEXT,
    SpecialOfferID INTEGER,
    UnitPrice REAL,
    UnitPriceDiscount REAL,
    LineTotal REAL,
    FOREIGN KEY (SalesOrderID) REFERENCES SalesOrderHeader (SalesOrderID)
);

CREATE INDEX IF NOT EXISTS idx_salesorderdetail_salesorderid
    ON SalesOrderDetail (SalesOrderID);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_conn() as conn:
        conn.executescript(SCHEMA_SQL)


def _row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def next_sales_order_id(conn):
    cur = conn.execute("SELECT MAX(SalesOrderID) AS max_id FROM SalesOrderHeader")
    row = cur.fetchone()
    max_id = row["max_id"] if row and row["max_id"] is not None else 50000
    return int(max_id) + 1


def seed_db():  # initialized data to th db if none
    with get_conn() as conn:
        cur = conn.execute("SELECT COUNT(1) AS count FROM SalesOrderHeader")
        if cur.fetchone()["count"] > 0:
            return
        headers = [
            {
                "SalesOrderID": 60001,
                "RevisionNumber": 0,
                "OrderDate": "2026-01-10",
                "DueDate": "2026-02-09",
                "ShipDate": "2026-01-12",
                "Status": 5,
                "OnlineOrderFlag": 1,
                "SalesOrderNumber": "SO60001",
                "PurchaseOrderNumber": "PO-1001",
                "AccountNumber": "AW00011015",
                "CustomerID": 11015,
                "SalesPersonID": None,
                "TerritoryID": None,
                "BillToAddressID": None,
                "ShipToAddressID": None,
                "ShipMethodID": None,
                "CreditCardID": None,
                "CreditCardApprovalCode": None,
                "CurrencyRateID": None,
                "SubTotal": 2325.00,
                "TaxAmt": 159.84,
                "Freight": 0.00,
                "TotalDue": 2484.84,
            },
            {
                "SalesOrderID": 60002,
                "RevisionNumber": 0,
                "OrderDate": "2026-01-12",
                "DueDate": "2026-02-11",
                "ShipDate": "2026-01-13",
                "Status": 5,
                "OnlineOrderFlag": 1,
                "SalesOrderNumber": "SO60002",
                "PurchaseOrderNumber": "PO-1002",
                "AccountNumber": "AW00011016",
                "CustomerID": 11016,
                "SalesPersonID": None,
                "TerritoryID": None,
                "BillToAddressID": None,
                "ShipToAddressID": None,
                "ShipMethodID": None,
                "CreditCardID": None,
                "CreditCardApprovalCode": None,
                "CurrencyRateID": None,
                "SubTotal": 499.00,
                "TaxAmt": 32.44,
                "Freight": 15.00,
                "TotalDue": 546.44,
            },
        ]

        details = [
            {
                "SalesOrderID": 60001,
                "CarrierTrackingNumber": "1Z999AA10123456784",
                "OrderQty": 15,
                "ProductID": "323",
                "ProductName": "Crown Race",
                "SpecialOfferID": None,
                "UnitPrice": 150.00,
                "UnitPriceDiscount": 0.0,
                "LineTotal": 2250.00,
            },
            {
                "SalesOrderID": 60001,
                "CarrierTrackingNumber": "1Z999AA10123456784",
                "OrderQty": 1,
                "ProductID": "2",
                "ProductName": "Bearing Ball",
                "SpecialOfferID": None,
                "UnitPrice": 75.00,
                "UnitPriceDiscount": 0.0,
                "LineTotal": 75.00,
            },
            {
                "SalesOrderID": 60002,
                "CarrierTrackingNumber": "1Z888BB10123456784",
                "OrderQty": 50,
                "ProductID": "1",
                "ProductName": "Adjustable Race",
                "SpecialOfferID": None,
                "UnitPrice": 9.98,
                "UnitPriceDiscount": 0.0,
                "LineTotal": 499.00,
            },
        ]

        documents = [
            {
                "SalesOrderID": 60001,
                "Filename": "seed-alpha.txt",
                "MimeType": "text/plain",
                "VendorName": "Northwind Outfitters",
                "InvoiceNumber": "INV-10045",
                "InvoiceDate": "2026-01-10",
                "DueDate": "2026-02-09",
                "Terms": "Net 30",
                "BillToName": "Engineered Bike Systems",
                "BillToAddress": "123 Camelia Avenue, Oxnard, CA 93030",
                "ShipToName": "Engineered Bike Systems Warehouse",
                "ShipToAddress": "99 Depot Rd, Oxnard, CA 93030",
                "Currency": "USD",
                "Notes": "Include invoice number on check.",
                "Subtotal": 2325.00,
                "Tax": 159.84,
                "Freight": 0.00,
                "Total": 2484.84,
                "RawText": None,
            },
            {
                "SalesOrderID": 60002,
                "Filename": "seed-bravo.txt",
                "MimeType": "text/plain",
                "VendorName": "Summit Components",
                "InvoiceNumber": "INV-10046",
                "InvoiceDate": "2026-01-12",
                "DueDate": "2026-02-11",
                "Terms": "Net 30",
                "BillToName": "Mechanical Products Ltd.",
                "BillToAddress": "22555 Paseo De Las Americas, San Diego, CA 92102",
                "ShipToName": "Mechanical Products Ltd.",
                "ShipToAddress": "22555 Paseo De Las Americas, San Diego, CA 92102",
                "Currency": "USD",
                "Notes": "Ground shipping.",
                "Subtotal": 499.00,
                "Tax": 32.44,
                "Freight": 15.00,
                "Total": 546.44,
                "RawText": None,
            },
        ]

        for header in headers:
            cols = ", ".join(header.keys())
            placeholders = ", ".join(["?"] * len(header))
            conn.execute(
                f"INSERT INTO SalesOrderHeader ({cols}) VALUES ({placeholders})",
                list(header.values()),
            )

        for detail in details:
            cols = ", ".join(detail.keys())
            placeholders = ", ".join(["?"] * len(detail))
            conn.execute(
                f"INSERT INTO SalesOrderDetail ({cols}) VALUES ({placeholders})",
                list(detail.values()),
            )

        for doc in documents:
            doc["CreatedAt"] = datetime.utcnow().isoformat()
            cols = ", ".join(doc.keys())
            placeholders = ", ".join(["?"] * len(doc))
            conn.execute(
                f"INSERT INTO Documents ({cols}) VALUES ({placeholders})",
                list(doc.values()),
            )


def fetch_orders(limit=25):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT h.*, d.InvoiceNumber, d.VendorName
            FROM SalesOrderHeader h
            LEFT JOIN Documents d ON d.SalesOrderID = h.SalesOrderID
            ORDER BY h.SalesOrderID DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [_row_to_dict(row) for row in rows]


def fetch_order(order_id):
    with get_conn() as conn:
        header = conn.execute(
            "SELECT * FROM SalesOrderHeader WHERE SalesOrderID = ?",
            (order_id,),
        ).fetchone()
        document = conn.execute(
            "SELECT * FROM Documents WHERE SalesOrderID = ?",
            (order_id,),
        ).fetchone()
        details = conn.execute(
            "SELECT * FROM SalesOrderDetail WHERE SalesOrderID = ?",
            (order_id,),
        ).fetchall()

    return {
        "header": _row_to_dict(header),
        "document": _row_to_dict(document),
        "details": [_row_to_dict(row) for row in details],
    }


def insert_order(payload):
    header = payload.get("header", {}) or {}
    document = payload.get("document", {}) or {}
    details = payload.get("details", []) or []

    with get_conn() as conn:
        sales_order_id = header.get("SalesOrderID") or next_sales_order_id(conn)
        header["SalesOrderID"] = sales_order_id

        header_values = {col: header.get(col) for col in HEADER_COLUMNS}
        cols = ", ".join(header_values.keys())
        placeholders = ", ".join(["?"] * len(header_values))
        conn.execute(
            f"INSERT INTO SalesOrderHeader ({cols}) VALUES ({placeholders})",
            list(header_values.values()),
        )

        if document:
            document = {**document}
            document["SalesOrderID"] = sales_order_id
            document["CreatedAt"] = datetime.utcnow().isoformat()
            doc_values = {col: document.get(col)
                          for col in DOCUMENT_COLUMNS if col != "DocumentID"}
            cols = ", ".join(doc_values.keys())
            placeholders = ", ".join(["?"] * len(doc_values))
            conn.execute(
                f"INSERT INTO Documents ({cols}) VALUES ({placeholders})",
                list(doc_values.values()),
            )

        for item in details:
            item = {**item, "SalesOrderID": sales_order_id}
            detail_values = {
                col: item.get(col) for col in DETAIL_COLUMNS if col != "SalesOrderDetailID"}
            cols = ", ".join(detail_values.keys())
            placeholders = ", ".join(["?"] * len(detail_values))
            conn.execute(
                f"INSERT INTO SalesOrderDetail ({cols}) VALUES ({placeholders})",
                list(detail_values.values()),
            )
    return fetch_order(sales_order_id)


def update_order(order_id, payload):
    header = payload.get("header", {}) or {}
    document = payload.get("document", {}) or {}
    details = payload.get("details", []) or []

    with get_conn() as conn:
        header["SalesOrderID"] = order_id
        assignments = ", ".join(
            [f"{col} = ?" for col in HEADER_COLUMNS if col != "SalesOrderID"])
        values = [header.get(col) for col in HEADER_COLUMNS if col != "SalesOrderID"]
        values.append(order_id)
        conn.execute(
            f"UPDATE SalesOrderHeader SET {assignments} WHERE SalesOrderID = ?",
            values,
        )

        existing_doc = conn.execute(
            "SELECT DocumentID FROM Documents WHERE SalesOrderID = ?",
            (order_id,),
        ).fetchone()

        if document:
            document = {**document}
            document["SalesOrderID"] = order_id
            if existing_doc:
                assignments = ", ".join(
                    [f"{col} = ?" for col in DOCUMENT_COLUMNS if col not in ("DocumentID", "CreatedAt")]
                )
                values = [
                    document.get(col) for col in DOCUMENT_COLUMNS if col not in (
                        "DocumentID", "CreatedAt")]
                values.append(order_id)
                conn.execute(
                    f"UPDATE Documents SET {assignments} WHERE SalesOrderID = ?",
                    values,
                )
            else:
                document["CreatedAt"] = datetime.utcnow().isoformat()
                doc_values = {col: document.get(
                    col) for col in DOCUMENT_COLUMNS if col != "DocumentID"}
                cols = ", ".join(doc_values.keys())
                placeholders = ", ".join(["?"] * len(doc_values))
                conn.execute(
                    f"INSERT INTO Documents ({cols}) VALUES ({placeholders})",
                    list(doc_values.values()),
                )

        conn.execute("DELETE FROM SalesOrderDetail WHERE SalesOrderID = ?", (order_id,))
        for item in details:
            item = {**item, "SalesOrderID": order_id}
            detail_values = {
                col: item.get(col) for col in DETAIL_COLUMNS if col != "SalesOrderDetailID"}
            cols = ", ".join(detail_values.keys())
            placeholders = ", ".join(["?"] * len(detail_values))
            conn.execute(
                f"INSERT INTO SalesOrderDetail ({cols}) VALUES ({placeholders})",
                list(detail_values.values()),
            )

    return fetch_order(order_id)


def db_snapshot(limit=10):
    with get_conn() as conn:
        headers = conn.execute(
            "SELECT * FROM SalesOrderHeader ORDER BY SalesOrderID DESC LIMIT ?",
            (limit,),
        ).fetchall()
        details = conn.execute(
            "SELECT * FROM SalesOrderDetail ORDER BY SalesOrderDetailID DESC LIMIT ?",
            (limit,),
        ).fetchall()
        documents = conn.execute(
            "SELECT * FROM Documents ORDER BY DocumentID DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return {
        "headers": [_row_to_dict(row) for row in headers],
        "details": [_row_to_dict(row) for row in details],
        "documents": [_row_to_dict(row) for row in documents],
    }
