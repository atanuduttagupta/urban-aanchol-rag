def build_knowledge_embedding_text(
    section_title: str | None,
    chunk_text: str | None,
) -> str:
    parts = []

    if section_title:
        parts.append(f"Section: {section_title.strip()}")

    if chunk_text:
        parts.append(chunk_text.strip())

    return "\n\n".join(parts)