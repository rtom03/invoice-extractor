from flask import Blueprint, jsonify, request

from db import db_snapshot, fetch_order, fetch_orders, insert_order, update_order
from llm import normalize_extraction

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/api/orders", methods=["GET", "POST"])
def orders():
    if request.method == "GET":
        limit = int(request.args.get("limit", 15))
        return jsonify(fetch_orders(limit=limit))

    payload = request.get_json(force=True, silent=True) or {}
    payload = normalize_extraction(payload)
    inserted = insert_order(payload)
    return jsonify(inserted), 201


@orders_bp.route("/api/orders/<int:order_id>", methods=["GET", "PUT"])
def order_detail(order_id):
    if request.method == "GET":
        return jsonify(fetch_order(order_id))

    payload = request.get_json(force=True, silent=True) or {}
    payload = normalize_extraction(payload)
    updated = update_order(order_id, payload)
    return jsonify(updated)


@orders_bp.route("/api/db_snapshot", methods=["GET"])
def snapshot():
    limit = int(request.args.get("limit", 10))
    return jsonify(db_snapshot(limit=limit))
