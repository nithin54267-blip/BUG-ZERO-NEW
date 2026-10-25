from flask import Blueprint, g, jsonify, request
from middleware.auth_middleware import token_required
from models import db

history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
@token_required
def history():
    return jsonify(reports=db.list_reports(g.user_id, (request.args.get("q") or "").strip()))


@history_bp.get("/history/<int:report_id>")
@token_required
def one(report_id):
    report = db.get_report(g.user_id, report_id)
    return (jsonify(report), 200) if report else (jsonify(error="Report not found."), 404)


@history_bp.delete("/history/<int:report_id>")
@token_required
def delete(report_id):
    if db.delete_report(g.user_id, report_id):
        return jsonify(ok=True)
    return jsonify(error="Report not found."), 404
