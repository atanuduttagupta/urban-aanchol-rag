from backend.app.catalogue.config import CATALOGUE_PATH
from backend.app.catalogue.pipeline import load_catalogue


def test_v1_1_loads_only_populated_products():
    products = load_catalogue(str(CATALOGUE_PATH))

    assert len(products) == 30

    product_ids = {product["product_id"] for product in products}

    assert "UA-0001" in product_ids
    assert "UA-0030" in product_ids

    assert "UA-0031" not in product_ids
    assert "UA-0050" not in product_ids