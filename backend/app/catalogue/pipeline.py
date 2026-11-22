
from .config import CATALOGUE_PATH
from .excel_reader import read_products
from .normalizer import normalize_products
from .validator import validate_products


def load_catalogue(file_path: str) -> list[dict]:
    """
    Read, validate, and normalize the product catalogue.

    Empty template rows are skipped by the Excel reader.
    Every remaining product row is validated strictly.
    """

    headers, products = read_products(file_path)

    errors = validate_products(products, headers)

    if errors:
        error_message = (
            f"Catalogue validation failed with {len(errors)} error(s):\n"
            + "\n".join(f"- {error}" for error in errors)
        )

        raise ValueError(error_message)

    return normalize_products(products)


def load_default_catalogue() -> list[dict]:
    """Load the configured default Urban Aanchol catalogue."""

    return load_catalogue(str(CATALOGUE_PATH))
