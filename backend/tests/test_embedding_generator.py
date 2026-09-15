from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.embedding_generator import EmbeddingGenerator
from backend.app.database.embedding_text import build_product_embedding_text


catalogue = load_default_catalogue()

product = next(
    product for product in catalogue
    if product["product_id"] == "UA-0001"
)

embedding_text = build_product_embedding_text(product)

generator = EmbeddingGenerator()
embedding = generator.generate(embedding_text)

print("Product ID:", product["product_id"])
print("Model dimensions:", generator.dimensions)
print("Embedding length:", len(embedding))
print("First 10 values:", embedding[:10])