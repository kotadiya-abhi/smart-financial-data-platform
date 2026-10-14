"""Records one row per pipeline run into pipeline_logs."""

from datetime import datetime


def start_run(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO pipeline_logs (started_at, status) VALUES (%s, 'running') RETURNING run_id",
            (datetime.now(),),
        )
        run_id = cur.fetchone()[0]
    conn.commit()
    return run_id


def finish_run(conn, run_id: int, status: str, records_processed: int, records_rejected: int, error_details: str | None = None) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE pipeline_logs
            SET finished_at = %s, status = %s, records_processed = %s,
                records_rejected = %s, error_details = %s
            WHERE run_id = %s
            """,
            (datetime.now(), status, records_processed, records_rejected, error_details, run_id),
        )
    conn.commit()
