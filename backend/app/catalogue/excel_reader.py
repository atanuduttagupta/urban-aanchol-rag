
from pathlib import Path

import openpyxl

REQUIRED_HEADERS = {
    "product_id",
    "product_name",
    "category",
}


def read_products(file_path: str) -> list[dict]:
    """
    Read product records from the Products sheet.

    The reader locates the header row by looking for required catalogue
    columns rather than assuming that the first row contains headers.

    Rows containing only a prefilled product_id and no other data
    are treated as empty template rows and skipped.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Catalogue file not found: {path}")

    workbook = openpyxl.load_workbook(
        path,
        read_only=True,
        data_only=True,
    )

    try:
        if "Products" not in workbook.sheetnames:
            raise ValueError(
                "Catalogue workbook does not contain a 'Products' sheet."
            )

        worksheet = workbook["Products"]
        rows = worksheet.iter_rows(values_only=True)

        headers = None

        for row in rows:
            normalized_headers = {
                str(value).strip()
                for value in row
                if value is not None
            }

            if REQUIRED_HEADERS.issubset(normalized_headers):
                headers = [
                    str(value).strip() if value is not None else ""
                    for value in row
                ]
                break

        if headers is None:
            raise ValueError(
                "Could not find the catalogue header row."
            )

        products = []

        for row in rows:
            product = dict(zip(headers, row, strict=False))

            other_values = [
                value
                for field, value in product.items()
                if field != "product_id"
            ]

            is_empty_row = all(
                value is None
                or (isinstance(value, str) and not value.strip())
                for value in other_values
            )

            if is_empty_row:
                continue

            products.append(product)

        return headers, products

    finally:
        workbook.close()