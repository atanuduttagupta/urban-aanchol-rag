from pathlib import Path

from excel_reader import read_products


CATALOGUE_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "catalogue"
    / "products_dummy.xlsx"
)


headers, products = read_products(str(CATALOGUE_PATH))
print(f"Headers found: {len(headers)}")

print(f"Products read: {len(products)}")

if products:
    print("First product:")
    print(products[0])