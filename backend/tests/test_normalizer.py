from backend.app.catalogue.config import CATALOGUE_PATH
from backend.app.catalogue.excel_reader import read_products
from backend.app.catalogue.normalizer import normalize_products


headers, products = read_products(str(CATALOGUE_PATH))

normalized_products = normalize_products(products)

print(f"Products normalized: {len(normalized_products)}")

if normalized_products:
    product = normalized_products[0]

    print("\nNormalized first product:")
    print(product)

    print("\nField types:")
    print(f"price: {type(product['price']).__name__}")
    print(f"launch_date: {type(product['launch_date']).__name__}")
    print(f"occasion: {type(product['occasion']).__name__}")
    print(f"tags: {type(product['tags']).__name__}")