from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.embedding_text import build_product_embedding_text


catalogue = load_default_catalogue()

product = next(
    product for product in catalogue
    if product["product_id"] == "UA-0001"
)

embedding_text = build_product_embedding_text(product)

print("Product ID:", product["product_id"])
print()
print(embedding_text)