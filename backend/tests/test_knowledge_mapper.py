from backend.app.database.knowledge_mapper import (
    map_knowledge_chunks,
    map_knowledge_document,
)


def main():
    document = map_knowledge_document(
        {
            "title": "Urban Aanchol Order & Policies",
            "document_type": "policy",
            "source": "Urban Aanchol",
            "language": "en",
            "status": "Active",
            "priority": 100,
        }
    )

    chunks = map_knowledge_chunks(
        [
            {
                "chunk_text": "Customers can place orders through WhatsApp.",
                "section_title": "How to Order",
            },
            {
                "chunk_text": "Delivery normally takes 5 to 7 working days.",
                "section_title": "Delivery",
            },
        ]
    )

    assert document["title"] == "Urban Aanchol Order & Policies"
    assert document["document_type"] == "policy"
    assert document["metadata"] == {}
    assert document["_created_at"] is not None
    assert document["_updated_at"] is not None

    assert len(chunks) == 2
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_index"] == 1
    assert chunks[0]["content_type"] == "text"
    assert chunks[0]["metadata"] == {}

    print("Knowledge document mapping passed.")
    print("Knowledge chunk mapping passed.")


if __name__ == "__main__":
    main()