from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator

from jobapply.config import DB_PATH, ensure_dirs


def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Application:
    id: int
    company: str
    title: str
    job_url: str
    source: str
    status: str
    match_category: str | None
    match_reason: str | None
    jd_text: str | None
    tailored_resume_path: str | None
    created_at: str
    updated_at: str


def init_db() -> None:
    ensure_dirs()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL DEFAULT '',
                title TEXT NOT NULL DEFAULT '',
                job_url TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Saved',
                match_category TEXT,
                match_reason TEXT,
                jd_text TEXT,
                tailored_resume_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def row_to_app(row: sqlite3.Row) -> Application:
    return Application(
        id=row["id"],
        company=row["company"] or "",
        title=row["title"] or "",
        job_url=row["job_url"] or "",
        source=row["source"] or "",
        status=row["status"] or "Saved",
        match_category=row["match_category"],
        match_reason=row["match_reason"],
        jd_text=row["jd_text"],
        tailored_resume_path=row["tailored_resume_path"],
        created_at=row["created_at"] or "",
        updated_at=row["updated_at"] or "",
    )


def list_applications(order: str = "updated_at DESC") -> list[Application]:
    init_db()
    allowed = {"updated_at DESC", "updated_at ASC", "created_at DESC"}
    if order not in allowed:
        order = "updated_at DESC"
    with get_conn() as conn:
        cur = conn.execute(f"SELECT * FROM applications ORDER BY {order}")
        return [row_to_app(r) for r in cur.fetchall()]


def get_application(app_id: int) -> Application | None:
    init_db()
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        row = cur.fetchone()
        return row_to_app(row) if row else None


def insert_application(
    *,
    company: str,
    title: str,
    job_url: str,
    source: str = "",
    status: str = "Saved",
    jd_text: str | None = None,
    match_category: str | None = None,
    match_reason: str | None = None,
    tailored_resume_path: str | None = None,
) -> int:
    init_db()
    now = _utc_now()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO applications (
                company, title, job_url, source, status,
                match_category, match_reason, jd_text, tailored_resume_path,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company,
                title,
                job_url,
                source,
                status,
                match_category,
                match_reason,
                jd_text,
                tailored_resume_path,
                now,
                now,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_application(app_id: int, fields: dict[str, Any]) -> None:
    init_db()
    if not fields:
        return
    keys = list(fields.keys())
    set_clause = ", ".join(f"{k} = ?" for k in keys)
    values = [fields[k] for k in keys] + [_utc_now(), app_id]
    with get_conn() as conn:
        conn.execute(
            f"UPDATE applications SET {set_clause}, updated_at = ? WHERE id = ?",
            values,
        )
        conn.commit()


def delete_application(app_id: int) -> None:
    init_db()
    with get_conn() as conn:
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
