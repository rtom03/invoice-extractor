export default function OrdersTable({
  orders,
  loading,
  error,
  onSelect,
}) {
  return (
    <div className="card" style={{ animationDelay: "0.08s" }}>
      <h2>Database Orders</h2>
      <p>Stored orders from the database. Click a row to view details.</p>
      {loading && <p className="status">Loading orders...</p>}
      {error && <p className="status">{error}</p>}
      {!loading && orders.length === 0 && (
        <p className="status">No orders yet. Save an extraction.</p>
      )}
      {orders.length > 0 && (
        <table className="table clickable">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Sales Order</th>
              <th>Invoice</th>
              <th>Vendor</th>
              <th>Customer</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.SalesOrderID} onClick={() => onSelect(order.SalesOrderID)}>
                <td>{order.SalesOrderID}</td>
                <td>{order.SalesOrderNumber || "-"}</td>
                <td>{order.InvoiceNumber || "-"}</td>
                <td>{order.VendorName || "-"}</td>
                <td>{order.CustomerID || "-"}</td>
                <td>${order.TotalDue ?? "0"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
