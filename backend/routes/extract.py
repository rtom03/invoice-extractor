import base64
import mimetypes
import os
from io import BytesIO
from time import perf_counter

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from llm import extract_invoice, normalize_extraction

extract_bp = Blueprint("extract", __name__)

UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
)


def extract_text_from_pdf(data):
    try:
        from pypdf import PdfReader
    except Exception:
        return None
    reader = PdfReader(BytesIO(data))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts).strip() or None


def load_text_from_file(data, filename, mime_type):
    if mime_type and mime_type.startswith("text/"):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="ignore")
    if filename and filename.lower().endswith((".txt", ".md", ".csv")):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="ignore")
    if filename and filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(data)
    return None


@extract_bp.route("/api/extract", methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]
    # print(file)
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    data = file.read()
    # print(data)
    mime_type = file.mimetype or mimetypes.guess_type(
        filename)[0] or "application/octet-stream"
    # print(mime_type)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(data)

    text = load_text_from_file(data, filename, mime_type)
    image_b64 = None
    # print(text)

    if mime_type.startswith("image/"):
        image_b64 = base64.b64encode(data).decode("ascii")
        # print(image_b64)

    if not text and not image_b64:
        return jsonify({"error": "Unsupported file type or empty content"}), 400

    start = perf_counter()
    extracted = extract_invoice(text=text, image_b64=image_b64, mime_type=mime_type)
    normalized = normalize_extraction(
        extracted,
        raw_text=text,
        filename=filename,
        mime_type=mime_type)
    normalized["meta"] = {"processing_ms": int((perf_counter() - start) * 1000)}

    return jsonify(normalized)
