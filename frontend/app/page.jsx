"use client";

import { useEffect, useState } from "react";
import ExtractionPanel from "./components/ExtractionPanel";
import OrderModal from "./components/OrderModal";
import OrdersTable from "./components/OrdersTable";
import UploadCard from "./components/UploadCard";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000";

const emptyExtraction = {
  document: {
    VendorName: "",
    InvoiceNumber: "",
    InvoiceDate: "",
    DueDate: "",
    Terms: "",
    BillToName: "",
    BillToAddress: "",
    ShipToName: "",
    ShipToAddress: "",
    Currency: "USD",
    Notes: "",
    Subtotal: "",
    Tax: "",
    Freight: "",
    Total: "",
  },
  header: {
    SalesOrderNumber: "",
    OrderDate: "",
    DueDate: "",
    ShipDate: "",
    PurchaseOrderNumber: "",
    AccountNumber: "",
    CustomerID: "",
    SalesPersonID: "",
    TerritoryID: "",
    BillToAddressID: "",
    ShipToAddressID: "",
    ShipMethodID: "",
    CreditCardID: "",
    CreditCardApprovalCode: "",
    CurrencyRateID: "",
    SubTotal: "",
    TaxAmt: "",
    Freight: "",
    TotalDue: "",
  },
  details: [],
};

export default function Home() {
  const [file, setFile] = useState(null);
  const [extraction, setExtraction] = useState(null);
  const [status, setStatus] = useState({ loading: false, message: "" });
  const [showResults, setShowResults] = useState(false);

  const [orders, setOrders] = useState([]);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [ordersError, setOrdersError] = useState("");
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState("");

  const fetchOrders = async () => {
    setOrdersLoading(true);
    setOrdersError("");
    try {
      const res = await fetch(`${API_BASE}/api/orders?limit=25`);
      const data = await res.json();
      // console.log(data);
      if (!res.ok) {
        throw new Error(data.error || "Failed to load orders.");
      }
      setOrders(data || []);
    } catch (error) {
      setOrdersError(error.message);
    } finally {
      setOrdersLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleExtract = async () => {
    if (!file) {
      setStatus({ loading: false, message: "Pick a file to extract." });
      return;
    }
    setStatus({ loading: true, message: "Running extraction..." });
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API_BASE}/api/extract`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Extraction failed.");
      }
      setExtraction(data);
      setShowResults(true);
      const runtime = data.meta?.processing_ms
        ? `${data.meta.processing_ms}ms`
        : "";
      setStatus({ loading: false, message: `Extraction complete ${runtime}` });
    } catch (error) {
      setStatus({ loading: false, message: error.message });
    }
  };

  const handleSave = async () => {
    if (!extraction) {
      return;
    }
    setStatus({ loading: true, message: "Saving to database..." });
    try {
      const res = await fetch(`${API_BASE}/api/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document: extraction.document,
          header: extraction.header,
          details: extraction.details,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Save failed.");
      }
      setExtraction(data);
      setStatus({
        loading: false,
        message: `Saved SalesOrderID ${data.header?.SalesOrderID}`,
      });
      fetchOrders();
    } catch (error) {
      setStatus({ loading: false, message: error.message });
    }
  };

  const openOrder = async (orderId) => {
    setModalOpen(true);
    setModalLoading(true);
    setModalError("");
    try {
      const res = await fetch(`${API_BASE}/api/orders/${orderId}`);
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to load order.");
      }
      setSelectedOrder(data);
    } catch (error) {
      setModalError(error.message);
      setSelectedOrder(null);
    } finally {
      setModalLoading(false);
    }
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedOrder(null);
    setModalError("");
  };

  const updateSection = (section, key, value) => {
    setExtraction((prev) => {
      const base = prev || emptyExtraction;
      return {
        ...base,
        [section]: {
          ...base[section],
          [key]: value,
        },
      };
    });
  };

  const updateDetail = (index, key, value) => {
    setExtraction((prev) => {
      const base = prev || emptyExtraction;
      const nextDetails = [...(base.details || [])];
      nextDetails[index] = { ...nextDetails[index], [key]: value };
      return { ...base, details: nextDetails };
    });
  };

  const addLineItem = () => {
    setExtraction((prev) => {
      const base = prev || emptyExtraction;
      const nextDetails = [...(base.details || [])];
      nextDetails.push({
        OrderQty: "",
        ProductID: "",
        ProductName: "",
        UnitPrice: "",
        UnitPriceDiscount: "",
        LineTotal: "",
        CarrierTrackingNumber: "",
        SpecialOfferID: "",
      });
      return { ...base, details: nextDetails };
    });
  };

  const removeLineItem = (index) => {
    setExtraction((prev) => {
      const base = prev || emptyExtraction;
      const nextDetails = [...(base.details || [])];
      nextDetails.splice(index, 1);
      return { ...base, details: nextDetails };
    });
  };

  const doc = extraction?.document || emptyExtraction.document;
  const header = extraction?.header || emptyExtraction.header;
  const details = extraction?.details || [];

  return (
    <main className="page">
      <header className="header">
        <div className="brand">
          <div className="brand-badge" />
          <div>
            <h1>Atlas Extract</h1>
            <p className="tagline">
              Invoice intelligence for SalesOrderHeader + SalesOrderDetail
            </p>
          </div>
        </div>
      </header>

      <section className="grid">
        <UploadCard
          onFileChange={(event) => setFile(event.target.files?.[0] || null)}
          onExtract={handleExtract}
          statusMessage={status.message}
          loading={status.loading}
        />
      </section>

      <section className="grid" style={{ marginTop: "24px" }}>
        <OrdersTable
          orders={orders}
          loading={ordersLoading}
          error={ordersError}
          onSelect={openOrder}
        />
      </section>

      {showResults && (
        <section className="grid" style={{ marginTop: "24px" }}>
          <ExtractionPanel
            doc={doc}
            header={header}
            details={details}
            onUpdateSection={updateSection}
            onUpdateDetail={updateDetail}
            onAddLineItem={addLineItem}
            onRemoveLineItem={removeLineItem}
            onSave={handleSave}
            saving={status.loading}
            canSave={Boolean(extraction)}
          />
        </section>
      )}

      <OrderModal
        open={modalOpen}
        onClose={closeModal}
        loading={modalLoading}
        error={modalError}
        order={selectedOrder}
      />
    </main>
  );
}
