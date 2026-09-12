from datetime import datetime, timezone


PRODUCT_FIELDS = (
    "product_id",
    "product_name",
    "category",
    "brand",
    "collection",
    "fabric",
    "colour",
    "secondary_colour",
    "pattern",
    "border",
    "price",
    "availability",
    "description",
    "product_url",
    "remarks",
    "additional_attributes",
    "launch_date",
    "created_at",
    "updated_at",
)


def map_product_to_database(product: dict) -> dict:
    now = datetime.now(timezone.utc)

    return {
        "product_id": product.get("product_id"),
        "product_name": product.get("product_name"),
        "category": product.get("category"),
        "brand": product.get("brand"),
        "collection": product.get("collection"),
        "fabric": product.get("fabric"),
        "colour": product.get("colour"),
        "secondary_colour": product.get("secondary_colour"),
        "pattern": product.get("pattern"),
        "border": product.get("border"),
        "price": product.get("price"),
        "availability": product.get("availability"),
        "description": product.get("description"),
        "product_url": product.get("product_url"),
        "remarks": product.get("remarks"),
        "additional_attributes": {},
        "launch_date": product.get("launch_date"),
        "created_at": now,
        "updated_at": now,
    }


def map_products_to_database(products: list[dict]) -> list[dict]:
    return [map_product_to_database(product) for product in products]