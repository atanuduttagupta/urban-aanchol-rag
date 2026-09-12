from datetime import date, datetime, timezone


def map_knowledge_document(document: dict) -> dict:
    now = datetime.now(timezone.utc)

    return {
        "title": document["title"],
        "document_type": document["document_type"],
        "source": document["source"],
        "source_url": document.get("source_url"),
        "language": document.get("language", "en"),
        "status": document.get("status", "Active"),
        "priority": document.get("priority", 0),
        "effective_from": document.get("effective_from"),
        "effective_to": document.get("effective_to"),
        "metadata": document.get("metadata", {}),
        "_created_at": now,
        "_updated_at": now,
    }


def map_knowledge_chunks(
    chunks: list[dict],
) -> list[dict]:
    mapped_chunks = []

    for index, chunk in enumerate(chunks):
        mapped_chunks.append(
            {
                "chunk_text": chunk["chunk_text"],
                "chunk_index": chunk.get("chunk_index", index),
                "section_title": chunk.get("section_title"),
                "content_type": chunk.get("content_type", "text"),
                "language": chunk.get("language", "en"),
                "token_count": chunk.get("token_count"),
                "metadata": chunk.get("metadata", {}),
            }
        )

    return mapped_chunks