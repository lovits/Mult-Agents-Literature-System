from __future__ import annotations

import json
import hashlib
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _encode(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _decode(payload: str | None) -> Any:
    return json.loads(payload) if payload else None


def _derived_version_id(paper_id: str, title: str, sections: list[dict[str, Any]], blocks: list[dict[str, Any]]) -> str:
    payload = _encode({"paper_id": paper_id, "title": title, "sections": sections, "blocks": blocks})
    return f"version-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:24]}"


class SQLiteRunRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    config_json TEXT NOT NULL,
                    input_json TEXT NOT NULL,
                    result_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL UNIQUE REFERENCES runs(run_id) ON DELETE CASCADE,
                    status TEXT NOT NULL,
                    progress REAL NOT NULL,
                    lease_expires_at TEXT,
                    attempt_token TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS job_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS paper_sections (
                    section_id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
                    ordinal INTEGER NOT NULL,
                    section_path TEXT NOT NULL,
                    section_type TEXT NOT NULL,
                    text TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence_blocks (
                    block_id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
                    ordinal INTEGER NOT NULL,
                    section_path TEXT NOT NULL,
                    section_type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    score REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS paper_versions (
                    version_id TEXT PRIMARY KEY,
                    paper_id TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
                    title TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS paper_active_versions (
                    paper_id TEXT PRIMARY KEY REFERENCES papers(paper_id) ON DELETE CASCADE,
                    version_id TEXT NOT NULL REFERENCES paper_versions(version_id)
                );
                CREATE TABLE IF NOT EXISTS paper_version_sections (
                    version_id TEXT NOT NULL REFERENCES paper_versions(version_id) ON DELETE CASCADE,
                    section_id TEXT NOT NULL,
                    paper_id TEXT NOT NULL,
                    ordinal INTEGER NOT NULL,
                    section_path TEXT NOT NULL,
                    section_type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    PRIMARY KEY(version_id, section_id)
                );
                CREATE TABLE IF NOT EXISTS paper_version_evidence_blocks (
                    version_id TEXT NOT NULL REFERENCES paper_versions(version_id) ON DELETE CASCADE,
                    block_id TEXT NOT NULL,
                    paper_id TEXT NOT NULL,
                    ordinal INTEGER NOT NULL,
                    section_path TEXT NOT NULL,
                    section_type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    score REAL NOT NULL,
                    PRIMARY KEY(version_id, block_id)
                );
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
                    paper_id TEXT NOT NULL,
                    metric_boundary TEXT NOT NULL,
                    artifact_path TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            self._backfill_paper_versions(connection)

    @staticmethod
    def _backfill_paper_versions(connection: sqlite3.Connection) -> None:
        papers = connection.execute(
            """
            SELECT papers.* FROM papers
            LEFT JOIN paper_active_versions ON paper_active_versions.paper_id = papers.paper_id
            WHERE paper_active_versions.paper_id IS NULL
            ORDER BY papers.paper_id
            """
        ).fetchall()
        for paper in papers:
            sections = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM paper_sections WHERE paper_id = ? ORDER BY ordinal, section_id",
                    (paper["paper_id"],),
                ).fetchall()
            ]
            blocks = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM evidence_blocks WHERE paper_id = ? ORDER BY ordinal, block_id",
                    (paper["paper_id"],),
                ).fetchall()
            ]
            version_id = _derived_version_id(str(paper["paper_id"]), str(paper["title"]), sections, blocks)
            connection.execute(
                """
                INSERT OR IGNORE INTO paper_versions(version_id, paper_id, title, source_type, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (version_id, paper["paper_id"], paper["title"], paper["source_type"], paper["updated_at"]),
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO paper_version_sections(
                    version_id, section_id, paper_id, ordinal, section_path, section_type, text
                ) VALUES (:version_id, :section_id, :paper_id, :ordinal, :section_path, :section_type, :text)
                """,
                [{**section, "version_id": version_id} for section in sections],
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO paper_version_evidence_blocks(
                    version_id, block_id, paper_id, ordinal, section_path, section_type, text, score
                ) VALUES (:version_id, :block_id, :paper_id, :ordinal, :section_path, :section_type, :text, :score)
                """,
                [{**block, "version_id": version_id} for block in blocks],
            )
            connection.execute(
                "INSERT INTO paper_active_versions(paper_id, version_id) VALUES (?, ?)",
                (paper["paper_id"], version_id),
            )

    def replace_paper_assets(
        self,
        paper_id: str,
        title: str,
        sections: list[dict[str, Any]],
        blocks: list[dict[str, Any]],
        version_id: str | None = None,
    ) -> None:
        timestamp = _now()
        resolved_version_id = version_id or _derived_version_id(paper_id, title, sections, blocks)
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute("SELECT created_at FROM papers WHERE paper_id = ?", (paper_id,)).fetchone()
            created_at = existing["created_at"] if existing else timestamp
            connection.execute(
                """
                INSERT INTO papers(paper_id, title, source_type, created_at, updated_at) VALUES (?, ?, 'markdown', ?, ?)
                ON CONFLICT(paper_id) DO UPDATE SET title = excluded.title, source_type = excluded.source_type,
                    updated_at = excluded.updated_at
                """,
                (paper_id, title, created_at, timestamp),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO paper_versions(version_id, paper_id, title, source_type, created_at)
                VALUES (?, ?, ?, 'markdown', ?)
                """,
                (resolved_version_id, paper_id, title, timestamp),
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO paper_version_sections(
                    version_id, section_id, paper_id, ordinal, section_path, section_type, text
                ) VALUES (:version_id, :section_id, :paper_id, :ordinal, :section_path, :section_type, :text)
                """,
                [{**section, "version_id": resolved_version_id} for section in sections],
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO paper_version_evidence_blocks(
                    version_id, block_id, paper_id, ordinal, section_path, section_type, text, score
                ) VALUES (:version_id, :block_id, :paper_id, :ordinal, :section_path, :section_type, :text, :score)
                """,
                [{**block, "version_id": resolved_version_id} for block in blocks],
            )
            connection.execute(
                """
                INSERT INTO paper_active_versions(paper_id, version_id) VALUES (?, ?)
                ON CONFLICT(paper_id) DO UPDATE SET version_id = excluded.version_id
                """,
                (paper_id, resolved_version_id),
            )
            connection.execute("DELETE FROM paper_sections WHERE paper_id = ?", (paper_id,))
            connection.execute("DELETE FROM evidence_blocks WHERE paper_id = ?", (paper_id,))
            connection.executemany(
                """
                INSERT INTO paper_sections(section_id, paper_id, ordinal, section_path, section_type, text)
                VALUES (:section_id, :paper_id, :ordinal, :section_path, :section_type, :text)
                """,
                sections,
            )
            connection.executemany(
                """
                INSERT INTO evidence_blocks(block_id, paper_id, ordinal, section_path, section_type, text, score)
                VALUES (:block_id, :paper_id, :ordinal, :section_path, :section_type, :text, :score)
                """,
                blocks,
            )

    def get_paper(self, paper_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM papers WHERE paper_id = ?", (paper_id,)).fetchone()
        if row is None:
            raise KeyError(f"paper not found: {paper_id}")
        paper = dict(row)
        paper["active_version_id"] = self.get_active_paper_version(paper_id)["version_id"]
        return paper

    def get_active_paper_version(self, paper_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT paper_versions.* FROM paper_active_versions
                JOIN paper_versions ON paper_versions.version_id = paper_active_versions.version_id
                WHERE paper_active_versions.paper_id = ?
                """,
                (paper_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"active paper version not found: {paper_id}")
        return dict(row)

    def list_paper_versions(self, paper_id: str) -> list[dict[str, Any]]:
        self.get_paper(paper_id)
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM paper_versions WHERE paper_id = ? ORDER BY created_at, version_id",
                (paper_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_paper_sections(self, paper_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM paper_sections WHERE paper_id = ? ORDER BY ordinal, section_id", (paper_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def list_evidence_blocks(self, paper_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM evidence_blocks WHERE paper_id = ? ORDER BY ordinal, block_id", (paper_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def list_evidence_block_ids(self, paper_id: str) -> list[str]:
        self.get_paper(paper_id)
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT block_id FROM evidence_blocks WHERE paper_id = ? ORDER BY ordinal, block_id", (paper_id,)
            ).fetchall()
        return [str(row["block_id"]) for row in rows]

    def get_evidence_blocks_by_ids(self, paper_id: str, block_ids: list[str]) -> list[dict[str, Any]]:
        if not block_ids:
            return []
        placeholders = ", ".join("?" for _ in block_ids)
        with self._connection() as connection:
            rows = connection.execute(
                f"SELECT * FROM evidence_blocks WHERE paper_id = ? AND block_id IN ({placeholders})",
                (paper_id, *block_ids),
            ).fetchall()
        by_id = {str(row["block_id"]): dict(row) for row in rows}
        missing = [block_id for block_id in block_ids if block_id not in by_id]
        if missing:
            raise KeyError(f"evidence block not found for paper {paper_id}: {missing[0]}")
        return [by_id[block_id] for block_id in block_ids]

    def list_version_evidence_blocks(self, paper_id: str, version_id: str) -> list[dict[str, Any]]:
        self._get_paper_version(paper_id, version_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM paper_version_evidence_blocks
                WHERE paper_id = ? AND version_id = ? ORDER BY ordinal, block_id
                """,
                (paper_id, version_id),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_version_evidence_block_ids(self, paper_id: str, version_id: str) -> list[str]:
        return [str(item["block_id"]) for item in self.list_version_evidence_blocks(paper_id, version_id)]

    def get_version_evidence_blocks_by_ids(
        self,
        paper_id: str,
        version_id: str,
        block_ids: list[str],
    ) -> list[dict[str, Any]]:
        self._get_paper_version(paper_id, version_id)
        if not block_ids:
            return []
        placeholders = ", ".join("?" for _ in block_ids)
        with self._connection() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM paper_version_evidence_blocks
                WHERE paper_id = ? AND version_id = ? AND block_id IN ({placeholders})
                """,
                (paper_id, version_id, *block_ids),
            ).fetchall()
        by_id = {str(row["block_id"]): dict(row) for row in rows}
        missing = [block_id for block_id in block_ids if block_id not in by_id]
        if missing:
            raise KeyError(f"version evidence block not found for paper {paper_id}: {missing[0]}")
        return [by_id[block_id] for block_id in block_ids]

    def _get_paper_version(self, paper_id: str, version_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM paper_versions WHERE paper_id = ? AND version_id = ?",
                (paper_id, version_id),
            ).fetchone()
        if row is None:
            raise KeyError(f"paper version not found: {paper_id}, {version_id}")
        return dict(row)

    def create_report(
        self,
        report_id: str,
        run_id: str,
        paper_id: str,
        metric_boundary: str,
        artifact_path: str,
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)",
                (report_id, run_id, paper_id, metric_boundary, artifact_path, _now()),
            )

    def get_report(self, report_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,)).fetchone()
        if row is None:
            raise KeyError(f"report not found: {report_id}")
        return dict(row)

    def create_run_and_job(self, run_id: str, job_id: str, input_payload: dict[str, Any]) -> None:
        timestamp = _now()
        config = {
            "top_k": input_payload.get("top_k", 5),
            "finding_top_k": input_payload.get("finding_top_k", 3),
            "workflow": "deterministic_review_audit_v1",
            "metric_boundary": "silver diagnostic",
        }
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT INTO runs VALUES (?, ?, 'queued', ?, ?, NULL, NULL, ?, ?)",
                (run_id, str(input_payload["paper_id"]), _encode(config), _encode(input_payload), timestamp, timestamp),
            )
            connection.execute(
                "INSERT INTO jobs VALUES (?, ?, 'queued', 0.0, NULL, NULL, NULL, ?, ?)",
                (job_id, run_id, timestamp, timestamp),
            )
            self._insert_event(connection, job_id, "queued", {"run_id": run_id})

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f"run not found: {run_id}")
        return self._run_dict(row)

    def list_runs(self) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute("SELECT * FROM runs ORDER BY created_at, run_id").fetchall()
        return [self._run_dict(row) for row in rows]

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(f"job not found: {job_id}")
        return dict(row)

    def get_job_for_run(self, run_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f"job not found for run: {run_id}")
        return dict(row)

    def list_events(self, job_id: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM job_events WHERE job_id = ? ORDER BY event_id", (job_id,)
            ).fetchall()
        return [
            {
                **dict(row),
                "payload": _decode(row["payload_json"]),
            }
            for row in rows
        ]

    def load_input(self, run_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT input_json FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f"run not found: {run_id}")
        return _decode(row["input_json"])

    def claim_next_job(self, lease_seconds: int = 300) -> dict[str, Any] | None:
        return self._claim_job(None, lease_seconds)

    def claim_job(self, job_id: str, lease_seconds: int = 300) -> dict[str, Any] | None:
        return self._claim_job(job_id, lease_seconds)

    def _claim_job(self, job_id: str | None, lease_seconds: int) -> dict[str, Any] | None:
        timestamp = _now()
        lease_expires_at = (datetime.now(UTC) + timedelta(seconds=lease_seconds)).isoformat()
        attempt_token = uuid4().hex
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if job_id is None:
                row = connection.execute(
                    "SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at, job_id LIMIT 1"
                ).fetchone()
            else:
                row = connection.execute(
                    "SELECT * FROM jobs WHERE job_id = ? AND status = 'queued'",
                    (job_id,),
                ).fetchone()
            if row is None:
                return None
            connection.execute(
                """
                UPDATE jobs SET status = 'running', progress = 0.1, lease_expires_at = ?, attempt_token = ?, updated_at = ?
                WHERE job_id = ? AND status = 'queued'
                """,
                (lease_expires_at, attempt_token, timestamp, row["job_id"]),
            )
            connection.execute(
                "UPDATE runs SET status = 'running', updated_at = ? WHERE run_id = ?",
                (timestamp, row["run_id"]),
            )
            self._insert_event(connection, row["job_id"], "running", {"progress": 0.1})
            return {
                **dict(row),
                "status": "running",
                "progress": 0.1,
                "lease_expires_at": lease_expires_at,
                "attempt_token": attempt_token,
            }

    def save_result(self, run_id: str, job_id: str, attempt_token: str, result: dict[str, Any]) -> None:
        timestamp = _now()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            pair = connection.execute(
                """
                SELECT runs.status AS run_status, jobs.status AS job_status, jobs.attempt_token
                FROM runs JOIN jobs ON jobs.run_id = runs.run_id
                WHERE runs.run_id = ? AND jobs.job_id = ?
                """,
                (run_id, job_id),
            ).fetchone()
            if pair is not None and pair["run_status"] == "succeeded" and pair["job_status"] == "succeeded":
                raise RuntimeError(f"run already succeeded: {run_id}")
            if pair is None or pair["run_status"] != "running" or pair["job_status"] != "running":
                raise RuntimeError(f"result requires matching running run and job: {run_id}, {job_id}")
            if pair["attempt_token"] != attempt_token:
                raise RuntimeError(f"result requires current attempt token: {job_id}")
            run_update = connection.execute(
                """
                UPDATE runs SET status = 'succeeded', result_json = ?, error = NULL, updated_at = ?
                WHERE run_id = ? AND status = 'running'
                """,
                (_encode(result), timestamp, run_id),
            )
            job_update = connection.execute(
                """
                UPDATE jobs SET status = 'succeeded', progress = 1.0, lease_expires_at = NULL, attempt_token = NULL,
                    error = NULL, updated_at = ?
                WHERE job_id = ? AND run_id = ? AND status = 'running' AND attempt_token = ?
                """,
                (timestamp, job_id, run_id, attempt_token),
            )
            if run_update.rowcount != 1 or job_update.rowcount != 1:
                raise RuntimeError(f"result requires matching running run and job: {run_id}, {job_id}")
            self._insert_event(connection, job_id, "succeeded", {"progress": 1.0})

    def mark_failed(self, run_id: str, job_id: str, attempt_token: str, error: str) -> bool:
        timestamp = _now()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            pair = connection.execute(
                """
                SELECT runs.status AS run_status, jobs.status AS job_status, jobs.attempt_token
                FROM runs JOIN jobs ON jobs.run_id = runs.run_id
                WHERE runs.run_id = ? AND jobs.job_id = ?
                """,
                (run_id, job_id),
            ).fetchone()
            if (
                pair is None
                or pair["run_status"] != "running"
                or pair["job_status"] != "running"
                or pair["attempt_token"] != attempt_token
            ):
                return False
            connection.execute(
                "UPDATE runs SET status = 'failed', error = ?, updated_at = ? WHERE run_id = ? AND status = 'running'",
                (error, timestamp, run_id),
            )
            connection.execute(
                """
                UPDATE jobs SET status = 'failed', lease_expires_at = NULL, attempt_token = NULL, error = ?, updated_at = ?
                WHERE job_id = ? AND run_id = ? AND status = 'running' AND attempt_token = ?
                """,
                (error, timestamp, job_id, run_id, attempt_token),
            )
            self._insert_event(connection, job_id, "failed", {"error": error})
            return True

    def mark_delivery_failed(self, run_id: str, job_id: str, error: str) -> bool:
        timestamp = _now()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            pair = connection.execute(
                """
                SELECT runs.status AS run_status, jobs.status AS job_status
                FROM runs JOIN jobs ON jobs.run_id = runs.run_id
                WHERE runs.run_id = ? AND jobs.job_id = ?
                """,
                (run_id, job_id),
            ).fetchone()
            if pair is None or pair["run_status"] != "queued" or pair["job_status"] != "queued":
                return False
            connection.execute(
                "UPDATE runs SET status = 'failed', error = ?, updated_at = ? WHERE run_id = ? AND status = 'queued'",
                (error, timestamp, run_id),
            )
            connection.execute(
                "UPDATE jobs SET status = 'failed', error = ?, updated_at = ? WHERE job_id = ? AND status = 'queued'",
                (error, timestamp, job_id),
            )
            self._insert_event(connection, job_id, "delivery_failed", {"error": error})
            return True

    def recover_running_jobs(self) -> int:
        timestamp = _now()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            rows = connection.execute(
                """
                SELECT job_id, run_id FROM jobs
                WHERE status = 'running' AND lease_expires_at IS NOT NULL AND lease_expires_at <= ?
                """,
                (timestamp,),
            ).fetchall()
            for row in rows:
                connection.execute(
                    """
                    UPDATE jobs SET status = 'queued', progress = 0.0, lease_expires_at = NULL, attempt_token = NULL,
                        updated_at = ?
                    WHERE job_id = ? AND status = 'running'
                    """,
                    (timestamp, row["job_id"]),
                )
                connection.execute(
                    "UPDATE runs SET status = 'queued', updated_at = ? WHERE run_id = ? AND status = 'running'",
                    (timestamp, row["run_id"]),
                )
                self._insert_event(connection, row["job_id"], "recovered", {"previous_status": "running"})
            return len(rows)

    @staticmethod
    def _insert_event(
        connection: sqlite3.Connection,
        job_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        connection.execute(
            "INSERT INTO job_events(job_id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)",
            (job_id, event_type, _encode(payload), _now()),
        )

    @staticmethod
    def _run_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {
            **dict(row),
            "config": _decode(row["config_json"]),
            "result": _decode(row["result_json"]),
        }
