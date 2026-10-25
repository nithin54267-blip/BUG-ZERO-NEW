import json
import os
import sqlite3
from config import Config


def get_conn():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    with get_conn() as conn, open(Config.SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
        # Upgrade databases created before the problem-statement feature existed.
        have = {r["name"] for r in conn.execute("PRAGMA table_info(reports)")}
        for col in ("problem_statement", "match_json"):
            if col not in have:
                conn.execute(f"ALTER TABLE reports ADD COLUMN {col} TEXT")


def create_user(username, email, password_hash):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        return cur.lastrowid


def find_user(identifier):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ? OR username = ?",
            (identifier.lower(), identifier),
        ).fetchone()


def user_exists(username, email):
    with get_conn() as conn:
        return conn.execute(
            "SELECT 1 FROM users WHERE username = ? OR email = ?", (username, email)
        ).fetchone() is not None


def save_report(user_id, language, code, report, problem_statement=None):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO reports (user_id, language, code, bugs_json, corrected_code, severity, "
            "problem_statement, match_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, language, code, json.dumps(report.get("bugs", [])),
             report.get("corrected_code", ""), report.get("overall_severity", "none"),
             problem_statement or None, json.dumps(report.get("requirements_match") or {})),
        )
        return cur.lastrowid


def _row_to_report(row, full=True):
    data = {
        "id": row["id"], "language": row["language"], "severity": row["severity"],
        "created_at": row["created_at"], "bug_count": len(json.loads(row["bugs_json"])),
    }
    if full:
        data.update(code=row["code"], bugs=json.loads(row["bugs_json"]),
                    corrected_code=row["corrected_code"],
                    problem_statement=row["problem_statement"] or "",
                    requirements_match=json.loads(row["match_json"] or "{}"))
    else:
        data["preview"] = row["code"][:120]
    return data


def list_reports(user_id, query=""):
    sql = "SELECT * FROM reports WHERE user_id = ?"
    args = [user_id]
    if query:
        sql += " AND (language LIKE ? OR code LIKE ? OR bugs_json LIKE ? OR problem_statement LIKE ?)"
        args += [f"%{query}%"] * 4
    sql += " ORDER BY created_at DESC, id DESC"
    with get_conn() as conn:
        return [_row_to_report(r, full=False) for r in conn.execute(sql, args).fetchall()]


def get_report(user_id, report_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ? AND user_id = ?", (report_id, user_id)
        ).fetchone()
        return _row_to_report(row) if row else None


def delete_report(user_id, report_id):
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM reports WHERE id = ? AND user_id = ?", (report_id, user_id)
        )
        return cur.rowcount > 0
