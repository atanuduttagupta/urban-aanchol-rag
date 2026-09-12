from backend.app.database.connection import get_database_connection


DOCUMENT_TITLE = "Urban Aanchol Order & Policies"

POLICY_ENTITIES = [
    ("policy_topic", "ordering", "Ordering"),
    ("policy_topic", "delivery", "Delivery"),
    ("policy_topic", "payment", "Payment"),
    ("policy_topic", "shipping", "Shipping"),
    ("policy_topic", "returns", "Returns"),
]


def main():
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:

            # Find the policy document.
            cursor.execute(
                """
                SELECT document_id
                FROM knowledge_documents
                WHERE title = %s
                  AND source = %s
                LIMIT 1
                """,
                (DOCUMENT_TITLE, "Urban Aanchol"),
            )

            document_row = cursor.fetchone()

            if not document_row:
                raise ValueError(
                    "Order & Policies document was not found."
                )

            document_id = document_row[0]

            # Create policy topic entities.
            for entity_type, entity_key, entity_name in POLICY_ENTITIES:
                cursor.execute(
                    """
                    INSERT INTO knowledge_entities (
                        entity_type,
                        entity_key,
                        entity_name
                    )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (entity_type, entity_key)
                    DO UPDATE SET
                        entity_name = EXCLUDED.entity_name
                    """,
                    (
                        entity_type,
                        entity_key,
                        entity_name,
                    ),
                )

            # Link the document to each policy topic.
            for entity_type, entity_key, _ in POLICY_ENTITIES:
                cursor.execute(
                    """
                    INSERT INTO knowledge_document_entities (
                        document_id,
                        entity_id,
                        relationship_type,
                        priority
                    )
                    SELECT
                        %s,
                        entity_id,
                        'applies_to',
                        100
                    FROM knowledge_entities
                    WHERE entity_type = %s
                      AND entity_key = %s
                    ON CONFLICT (
                        document_id,
                        entity_id,
                        relationship_type
                    )
                    DO NOTHING
                    """,
                    (
                        document_id,
                        entity_type,
                        entity_key,
                    ),
                )

        connection.commit()

        print("Order & Policies graph links created successfully.")
        print(f"Policy topics linked: {len(POLICY_ENTITIES)}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()