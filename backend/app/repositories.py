from typing import Any

from app.db import get_connection


def create_document(document_id: str, filename: str, stored_path: str) -> dict[str, Any]:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO documents (id, filename, stored_path, status)
            VALUES (?, ?, ?, ?)
            """,
            (document_id, filename, stored_path, "processing"),
        )
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
    return dict(row)


def update_document_status(
    document_id: str,
    status: str,
    error_message: str | None = None,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE documents
            SET status = ?, error_message = ?
            WHERE id = ?
            """,
            (status, error_message, document_id),
        )


def get_document(document_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
    return dict(row) if row else None


def list_documents() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT d.*,
                   COUNT(c.id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.uploaded_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def create_chunks(chunks: list[dict[str, Any]]) -> None:
    if not chunks:
        return

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO chunks (
                id, document_id, chunk_index, text, page_number, embedding_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    chunk["id"],
                    chunk["document_id"],
                    chunk["chunk_index"],
                    chunk["text"],
                    chunk["page_number"],
                    chunk["embedding_id"],
                )
                for chunk in chunks
            ],
        )


def get_chunks_by_ids(chunk_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not chunk_ids:
        return {}

    placeholders = ",".join("?" for _ in chunk_ids)
    query = f"""
        SELECT c.*, d.filename
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE c.id IN ({placeholders})
    """
    with get_connection() as conn:
        rows = conn.execute(query, chunk_ids).fetchall()
    return {row["id"]: dict(row) for row in rows}
