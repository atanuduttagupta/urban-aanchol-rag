from typing import Iterable

from psycopg import Connection
from psycopg.types.json import Jsonb


def insert_knowledge_document(
    connection: Connection,
    document: dict,
) -> str:
    sql = """
        INSERT INTO knowledge_documents (
            title,
            document_type,
            source,
            source_url,
            language,
            status,
            priority,
            effective_from,
            effective_to,
            metadata
        )
        VALUES (
            %(title)s,
            %(document_type)s,
            %(source)s,
            %(source_url)s,
            %(language)s,
            %(status)s,
            %(priority)s,
            %(effective_from)s,
            %(effective_to)s,
            %(metadata)s
        )
        RETURNING document_id
    """

    document_data = document.copy()
    document_data["metadata"] = Jsonb(
        document_data.get("metadata", {})
    )

    with connection.cursor() as cursor:
        cursor.execute(sql, document_data)
        return str(cursor.fetchone()[0])


def insert_knowledge_chunks(
    connection: Connection,
    document_id: str,
    chunks: Iterable[dict],
) -> int:
    sql = """
        INSERT INTO knowledge_chunks (
            document_id,
            chunk_text,
            chunk_index,
            section_title,
            content_type,
            language,
            token_count,
            metadata
        )
        VALUES (
            %(document_id)s,
            %(chunk_text)s,
            %(chunk_index)s,
            %(section_title)s,
            %(content_type)s,
            %(language)s,
            %(token_count)s,
            %(metadata)s
        )
        ON CONFLICT (document_id, chunk_index) DO UPDATE SET
            chunk_text = EXCLUDED.chunk_text,
            section_title = EXCLUDED.section_title,
            content_type = EXCLUDED.content_type,
            language = EXCLUDED.language,
            token_count = EXCLUDED.token_count,
            metadata = EXCLUDED.metadata
    """

    count = 0

    with connection.cursor() as cursor:
        for chunk in chunks:
            chunk_data = {
                "document_id": document_id,
                **chunk,
            }

            chunk_data["metadata"] = Jsonb(
                chunk_data.get("metadata", {})
            )

            cursor.execute(sql, chunk_data)
            count += 1

    return count