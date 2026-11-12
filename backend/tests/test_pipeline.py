from backend.app.catalogue.pipeline import load_default_catalogue


products = load_default_catalogue()

print(f"Products loaded through pipeline: {len(products)}")

if products:
    product = products[0]

    print("\nFirst normalized product:")
    print(product)