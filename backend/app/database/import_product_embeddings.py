from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.connection import get_database_connection
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.database.embedding_repository import save_product_embedding
from backend.app.database.embedding_text import build_product_embedding_text


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_VERSION = "v1"


def import_product_embeddings() -> None:
    catalogue = load_default_catalogue()

    print(f"Products loaded: {len(catalogue)}")

    generator = EmbeddingGenerator()

    connection = get_database_connection()

    try:
        saved_count = 0

        for product in catalogue:
            embedding_text = build_product_embedding_text(product)
            embedding = generator.generate(embedding_text)

            save_product_embedding(
                connection=connection,
                product_id=product["product_id"],
                model_name=MODEL_NAME,
                model_version=MODEL_VERSION,
                embedding=embedding,
                dimensions=generator.dimensions,
            )

            saved_count += 1
            print(
                f"Embedded: {product['product_id']} - "
                f"{product['product_name']}"
            )

        connection.commit()

        print()
        print(f"Embeddings saved: {saved_count}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    import_product_embeddings()