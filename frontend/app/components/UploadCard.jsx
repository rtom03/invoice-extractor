export default function UploadCard({
  onFileChange,
  onExtract,
  statusMessage,
  loading,
}) {
  return (
    <div className="card" style={{ animationDelay: "0.05s" }}>
      <h2>Upload & Extract</h2>
      <p>
        Drop an invoice (PNG, PDF, or text) to extract structured data with your
        LLM API.
      </p>
      <div className="dropzone">
        <strong>Choose a file</strong>
        <input
          className="file-input"
          type="file"
          accept=".png,.jpg,.jpeg,.pdf,.txt,.md,.csv"
          onChange={onFileChange}
        />
      </div>
      <div className="button-row" style={{ marginTop: "16px" }}>
        <button className="button" onClick={onExtract} disabled={loading}>
          Run Extraction
        </button>
      </div>
      <p className="status">{statusMessage}</p>
      <div className="status">
        <span className="pill">Sample invoices in /sample_invoices</span>
      </div>
    </div>
  );
}
