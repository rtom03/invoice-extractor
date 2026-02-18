export default function OrderModal({
  open,
  onClose,
  loading,
  error,
  order,
  setModalOpen,
}) {
  if (!open) {
    return null;
  }
  const API_BASE =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000/api/orders";
  const header = order?.header || {};
  const doc = order?.document || {};
  const details = order?.details || [];

  const removeInvoice = async (id) => {
    try {
      const request = await fetch(`${API_BASE}/${id}`, {
        method: "DELETE",
      });
      if (!request.ok) {
        throw new Error(data.error || "Failed to load orders.");
      }
      setModalOpen(false);
      const response = await request.json();
      return response;
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h3>Order {header.SalesOrderID || "-"}</h3>
            <p>{doc.VendorName || "Vendor not set"}</p>
          </div>
          <div className="m-btn">
            <button
              className="button secondary"
              style={{ backgroundColor: "red" }}
              onClick={() => removeInvoice(header.SalesOrderID)}
            >
              Delete
            </button>
            <button className="button secondary" onClick={onClose}>
              Close
            </button>
          </div>
        </div>

        {loading && <p className="status">Loading order...</p>}
        {error && <p className="status">{error}</p>}

        {!loading && !error && (
          <div className="modal-body">
            <div className="modal-grid">
              <div className="modal-section">
                <h4>Document</h4>
                <p>Invoice: {doc.InvoiceNumber || "-"}</p>
                <p>Invoice Date: {doc.InvoiceDate || "-"}</p>
                <p>Due Date: {doc.DueDate || "-"}</p>
                <p>Terms: {doc.Terms || "-"}</p>
              </div>
              <div className="modal-section">
                <h4>Totals</h4>
                <p>Subtotal: ${doc.Subtotal ?? "0"}</p>
                <p>Tax: ${doc.Tax ?? "0"}</p>
                <p>Freight: ${doc.Freight ?? "0"}</p>
                <p>Total: ${doc.Total ?? "0"}</p>
              </div>
              <div className="modal-section">
                <h4>Customer</h4>
                <p>Customer ID: {header.CustomerID || "-"}</p>
                <p>Account: {header.AccountNumber || "-"}</p>
                <p>Bill To: {doc.BillToName || "-"}</p>
                <p>Ship To: {doc.ShipToName || "-"}</p>
              </div>
            </div>

            <div style={{ marginTop: "16px" }}>
              <h4>Line Items</h4>
              {details.length === 0 ? (
                <p className="status">No line items stored.</p>
              ) : (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Qty</th>
                      <th>Product ID</th>
                      <th>Description</th>
                      <th>Unit</th>
                      <th>Line Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {details.map((item) => (
                      <tr key={item.SalesOrderDetailID || item.ProductID}>
                        <td>{item.OrderQty ?? "-"}</td>
                        <td>{item.ProductID ?? "-"}</td>
                        <td>{item.ProductName ?? "-"}</td>
                        <td>${item.UnitPrice ?? "0"}</td>
                        <td>${item.LineTotal ?? "0"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
