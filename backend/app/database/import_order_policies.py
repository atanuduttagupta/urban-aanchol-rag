from backend.app.database.connection import get_database_connection
from backend.app.database.knowledge_mapper import (
    map_knowledge_chunks,
    map_knowledge_document,
)
from backend.app.database.knowledge_repository import (
    insert_knowledge_chunks,
    insert_knowledge_document,
)


DOCUMENT = {
    "title": "Urban Aanchol Order & Policies",
    "document_type": "policy",
    "source": "Urban Aanchol",
    "language": "en",
    "status": "Active",
    "priority": 100,
    "metadata": {
        "scope": "global",
        "managed_by": "boutique",
    },
}


CHUNKS = [
    {
        "chunk_text": (
            "Customers can place orders through WhatsApp. "
            "Product availability is confirmed before the order is finalized. "
            "Orders require prepayment through online payment methods."
        ),
        "section_title": "How to Order",
    },
    {
        "chunk_text": (
            "Delivery normally takes 5 to 7 working days "
            "after order confirmation."
        ),
        "section_title": "Delivery",
    },
    {
        "chunk_text": (
            "Online payment is required. "
            "Cash on Delivery is not available."
        ),
        "section_title": "Payment",
    },
    {
        "chunk_text": (
            "Shipping is free within West Bengal. "
            "Shipping charges apply for deliveries outside West Bengal."
        ),
        "section_title": "Shipping Charges",
    },
    {
        "chunk_text": (
            "Returns are accepted only for products that are physically "
            "damaged on delivery. Customers must provide a clear unboxing "
            "video showing the damage."
        ),
        "section_title": "Returns",
    },
]


def find_existing_document(connection, title: str) -> str | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT document_id
            FROM knowledge_documents
            WHERE title = %s
              AND source = %s
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (title, "Urban Aanchol"),
        )

        row = cursor.fetchone()
        return str(row[0]) if row else None


def main():
    document = map_knowledge_document(DOCUMENT)
    chunks = map_knowledge_chunks(CHUNKS)

    connection = get_database_connection()

    try:
        document_id = find_existing_document(
            connection,
            document["title"],
        )

        if document_id:
            print(f"Existing document found: {document_id}")
        else:
            document_id = insert_knowledge_document(
                connection,
                document,
            )
            print(f"Created document: {document_id}")

        processed_chunks = insert_knowledge_chunks(
            connection,
            document_id,
            chunks,
        )

        connection.commit()

        print(f"Policy chunks processed: {processed_chunks}")
        print("Order & Policies import completed successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()