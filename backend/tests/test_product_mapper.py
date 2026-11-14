
from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.product_mapper import (
    PRODUCT_FIELDS,
    map_products_to_database,
)


def main():
    products = load_default_catalogue()
    mapped_products = map_products_to_database(products)

    print(f"Products loaded: {len(products)}")
    print(f"Products mapped: {len(mapped_products)}")

    assert len(mapped_products) == 30

    for product in mapped_products:
        assert set(product.keys()) == set(PRODUCT_FIELDS)
        assert product["product_id"]
        assert product["product_name"]
        assert product["additional_attributes"] == {}
        assert product["created_at"] is not None
        assert product["updated_at"] is not None

        # Inventory mapping checks
        assert isinstance(product["stock_quantity"], int)
        assert not isinstance(product["stock_quantity"], bool)
        assert product["stock_quantity"] >= 0

        # Existing field exclusions
        assert "image_url" not in product
        assert "video_url" not in product
        assert "occasion" not in product
        assert "style" not in product
        assert "mood" not in product
        assert "tags" not in product

    print("Product mapping validation passed.")
    print("\nFirst mapped product:")
    for field, value in mapped_products[0].items():
        print(f"{field}: {value}")


if __name__ == "__main__":
    main()
