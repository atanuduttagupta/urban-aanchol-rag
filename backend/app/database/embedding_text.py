def build_product_embedding_text(product: dict) -> str:
    parts = [
        f"Product: {product.get('product_name') or ''}",
        f"Category: {product.get('category') or ''}",
        f"Brand: {product.get('brand') or ''}",
        f"Collection: {product.get('collection') or ''}",
        f"Fabric: {product.get('fabric') or ''}",
        f"Colour: {product.get('colour') or ''}",
        f"Secondary colour: {product.get('secondary_colour') or ''}",
        f"Pattern: {product.get('pattern') or ''}",
        f"Border: {product.get('border') or ''}",
        f"Description: {product.get('description') or ''}",
        f"Remarks: {product.get('remarks') or ''}",
    ]

    return "\n".join(parts)