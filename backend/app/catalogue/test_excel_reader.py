from backend.app.catalogue.config import CATALOGUE_PATH
from backend.app.catalogue.excel_reader import read_products


headers, products = read_products(str(CATALOGUE_PATH))

print(f"Headers found: {len(headers)}")
print(f"Products read: {len(products)}")

if products:
    print("First product:")
    print(products[0])