export default function ExtractionPanel({
  doc,
  header,
  details,
  onUpdateSection,
  onUpdateDetail,
  onAddLineItem,
  onRemoveLineItem,
  onSave,
  saving,
  canSave,
}) {
  return (
    <div className="card" style={{ animationDelay: "0.1s" }}>
      <h2>Invoice Metadata + Line Items</h2>
      <p>Review extracted metadata and line-level details.</p>

      <div className="field-grid">
        <div className="field">
          <label>Vendor Name</label>
          <input
            value={doc.VendorName || ""}
            onChange={(event) =>
              onUpdateSection("document", "VendorName", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Invoice Number</label>
          <input
            value={doc.InvoiceNumber || ""}
            onChange={(event) =>
              onUpdateSection("document", "InvoiceNumber", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Invoice Date</label>
          <input
            value={doc.InvoiceDate || ""}
            onChange={(event) =>
              onUpdateSection("document", "InvoiceDate", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Due Date</label>
          <input
            value={doc.DueDate || ""}
            onChange={(event) =>
              onUpdateSection("document", "DueDate", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Terms</label>
          <input
            value={doc.Terms || ""}
            onChange={(event) =>
              onUpdateSection("document", "Terms", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Currency</label>
          <input
            value={doc.Currency || ""}
            onChange={(event) =>
              onUpdateSection("document", "Currency", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Sales Order Number</label>
          <input
            value={header.SalesOrderNumber || ""}
            onChange={(event) =>
              onUpdateSection("header", "SalesOrderNumber", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Purchase Order</label>
          <input
            value={header.PurchaseOrderNumber || ""}
            onChange={(event) =>
              onUpdateSection(
                "header",
                "PurchaseOrderNumber",
                event.target.value,
              )
            }
          />
        </div>
        <div className="field">
          <label>Account Number</label>
          <input
            value={header.AccountNumber || ""}
            onChange={(event) =>
              onUpdateSection("header", "AccountNumber", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Customer ID</label>
          <input
            value={header.CustomerID ?? ""}
            onChange={(event) =>
              onUpdateSection("header", "CustomerID", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Subtotal</label>
          <input
            value={doc.Subtotal ?? ""}
            onChange={(event) =>
              onUpdateSection("document", "Subtotal", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Tax</label>
          <input
            value={doc.Tax ?? ""}
            onChange={(event) =>
              onUpdateSection("document", "Tax", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Freight</label>
          <input
            value={doc.Freight ?? ""}
            onChange={(event) =>
              onUpdateSection("document", "Freight", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Total</label>
          <input
            value={doc.Total ?? ""}
            onChange={(event) =>
              onUpdateSection("document", "Total", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Bill To</label>
          <input
            value={doc.BillToName || ""}
            onChange={(event) =>
              onUpdateSection("document", "BillToName", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Ship To</label>
          <input
            value={doc.ShipToName || ""}
            onChange={(event) =>
              onUpdateSection("document", "ShipToName", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Bill To Address</label>
          <textarea
            value={doc.BillToAddress || ""}
            onChange={(event) =>
              onUpdateSection("document", "BillToAddress", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Ship To Address</label>
          <textarea
            value={doc.ShipToAddress || ""}
            onChange={(event) =>
              onUpdateSection("document", "ShipToAddress", event.target.value)
            }
          />
        </div>
        <div className="field">
          <label>Notes</label>
          <textarea
            value={doc.Notes || ""}
            onChange={(event) =>
              onUpdateSection("document", "Notes", event.target.value)
            }
          />
        </div>
      </div>

      <div style={{ marginTop: "20px" }}>
        <h3 style={{ marginBottom: "8px" }}>Line Items</h3>
        <div className="line-items">
          {details.length === 0 ? (
            <p className="status">No line items yet.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Qty</th>
                  <th>Product ID</th>
                  <th>Description</th>
                  <th>Unit</th>
                  <th>Line Total</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {details.map((item, index) => (
                  <tr key={`line-${index}`}>
                    <td>
                      <input
                        value={item.OrderQty ?? ""}
                        onChange={(event) =>
                          onUpdateDetail(index, "OrderQty", event.target.value)
                        }
                      />
                    </td>
                    <td>
                      <input
                        value={item.ProductID ?? ""}
                        onChange={(event) =>
                          onUpdateDetail(index, "ProductID", event.target.value)
                        }
                      />
                    </td>
                    <td>
                      <input
                        value={item.ProductName ?? ""}
                        onChange={(event) =>
                          onUpdateDetail(
                            index,
                            "ProductName",
                            event.target.value,
                          )
                        }
                      />
                    </td>
                    <td>
                      <input
                        value={item.UnitPrice ?? ""}
                        onChange={(event) =>
                          onUpdateDetail(index, "UnitPrice", event.target.value)
                        }
                      />
                    </td>
                    <td>
                      <input
                        value={item.LineTotal ?? ""}
                        onChange={(event) =>
                          onUpdateDetail(index, "LineTotal", event.target.value)
                        }
                      />
                    </td>
                    <td>
                      <button
                        className="button secondary"
                        onClick={() => onRemoveLineItem(index)}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className="button-row">
            <button className="button secondary" onClick={onAddLineItem}>
              Add Line Item
            </button>
          </div>
        </div>
      </div>

      <div className="button-row" style={{ marginTop: "20px" }}>
        <button
          className="button"
          onClick={onSave}
          disabled={!canSave || saving}
        >
          Save to Database
        </button>
      </div>
    </div>
  );
}
