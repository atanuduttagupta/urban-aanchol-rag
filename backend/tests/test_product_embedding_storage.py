from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.connection import get_database_connection
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.database.embedding_repository import save_product_embedding
from backend.app.database.embedding_text import build_product_embedding_text


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_VERSION = "v1"


catalogue = load_default_catalogue()

product = next(
    product for product in catalogue
    if product["product_id"] == "UA-0001"
)

embedding_text = build_product_embedding_text(product)

generator = EmbeddingGenerator()
embedding = generator.generate(embedding_text)

connection = get_database_connection()

try:
    embedding_id = save_product_embedding(
        connection=connection,
        product_id=product["product_id"],
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        embedding=embedding,
        dimensions=generator.dimensions,
    )

    connection.commit()

    print("Embedding saved successfully.")
    print("Product ID:", product["product_id"])
    print("Embedding ID:", embedding_id)
    print("Dimensions:", generator.dimensions)

finally:
    connection.close()