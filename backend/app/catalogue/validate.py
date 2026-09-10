from pathlib import Path

from .excel_reader import read_products
from .validator import validate_products


CATALOGUE_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "catalogue"
    / "products_dummy.xlsx"
)


def main() -> None:
    """Validate the Urban Aanchol product catalogue."""

    print("Urban Aanchol Catalogue Validation")
    print("----------------------------------")

    try:
        headers, products = read_products(str(CATALOGUE_PATH))
        errors = validate_products(products, headers)

    except Exception as error:
        print(f"Validation could not be completed: {error}")
        return

    print(f"Products checked: {len(products)}")
    print(f"Validation errors: {len(errors)}")

    if errors:
        print("\nValidation errors:")

        for error in errors:
            print(f"- {error}")

        return

    print("\nCatalogue validation passed.")


if __name__ == "__main__":
    main()