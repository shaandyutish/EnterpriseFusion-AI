import sqlite3
import json
from datetime import datetime
from config import DB_PATH, logger


def get_connection():
    """Return a SQLite connection; caller must close()."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create required tables if they do not exist."""
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Tickets table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT,
                customer_id TEXT,
                channel TEXT,
                message TEXT,
                intent TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT,
                resolved_at TEXT,
                agent_result_json TEXT
            );
            """
        )

        # Data quality runs table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS data_quality_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT,
                uploaded_by TEXT,
                uploaded_at TEXT,
                row_count INTEGER,
                issue_count INTEGER,
                score REAL,
                result_json TEXT
            );
            """
        )

        conn.commit()
        logger.info("DB init: tickets and data_quality_runs tables ready")
    finally:
        conn.close()


# ---------------- Tickets helpers ----------------


def create_ticket_from_result(result: dict):
    """
    Save a ticket agent result dict into the tickets table.

    Expected keys in result (best-effort, all optional except ticket_id/message):
    - ticket_id
    - customer_id
    - channel
    - message
    - intent
    - priority
    - status (or decision -> mapped)
    - created_at (optional)
    - resolved_at (optional)
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        ticket_id = result.get("ticket_id")
        customer_id = result.get("customer_id")
        channel = result.get("channel")
        message = result.get("message")
        intent = result.get("intent")
        priority = result.get("priority")

        # Derive status from decision if not provided
        status = result.get("status")
        if not status:
            decision = (result.get("decision") or "").upper()
            if decision in {"AUTO_RESOLVE", "RESOLVED"}:
                status = "resolved"
            elif decision in {"ESCALATE", "ROUTE_TO_HUMAN"}:
                status = "escalated"
            else:
                status = "open"

        created_at = result.get("created_at") or datetime.utcnow().isoformat()
        resolved_at = result.get("resolved_at")

        agent_result_json = json.dumps(result, ensure_ascii=False)

        cur.execute(
            """
            INSERT INTO tickets (
                ticket_id,
                customer_id,
                channel,
                message,
                intent,
                priority,
                status,
                created_at,
                resolved_at,
                agent_result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                customer_id,
                channel,
                message,
                intent,
                priority,
                status,
                created_at,
                resolved_at,
                agent_result_json,
            ),
        )
        conn.commit()
        logger.info("Ticket saved to DB", extra={"ticket_id": ticket_id})
    finally:
        conn.close()


def list_tickets_for_customer(customer_id: str, limit: int = 10):
    """Return recent tickets for a customer as list[dict]."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                ticket_id,
                customer_id,
                channel,
                message,
                intent,
                priority,
                status,
                created_at,
                resolved_at
            FROM tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (customer_id, limit),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------- Data quality helpers ----------------


def save_data_quality_run(
    dataset_name: str,
    uploaded_by: str,
    row_count: int,
    issue_count: int,
    score: float,
    result: dict,
):
    """Insert one data quality run into the DB."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        uploaded_at = datetime.utcnow().isoformat()
        result_json = json.dumps(result, ensure_ascii=False)

        cur.execute(
            """
            INSERT INTO data_quality_runs (
                dataset_name,
                uploaded_by,
                uploaded_at,
                row_count,
                issue_count,
                score,
                result_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_name,
                uploaded_by,
                uploaded_at,
                row_count,
                issue_count,
                score,
                result_json,
            ),
        )
        conn.commit()
        logger.info(
            "Saved data_quality_run",
            extra={"dataset_name": dataset_name, "row_count": row_count, "score": score},
        )
    finally:
        conn.close()


def list_data_quality_runs(limit: int = 10):
    """Return recent data quality runs as list[dict]."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                id,
                dataset_name,
                uploaded_by,
                uploaded_at,
                row_count,
                issue_count,
                score
            FROM data_quality_runs
            ORDER BY uploaded_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
