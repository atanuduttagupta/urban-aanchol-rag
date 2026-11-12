from backend.app.catalogue.config import CATALOGUE_PATH
from backend.app.catalogue.excel_reader import read_products
from backend.app.catalogue.validator import validate_products


headers, products = read_products(str(CATALOGUE_PATH))

errors = validate_products(products, headers)

print(f"Products validated: {len(products)}")
print(f"Validation errors: {len(errors)}")

if errors:
    print("\nValidation errors:")
    for error in errors:
        print(f"- {error}")
else:
    print("Catalogue validation passed.")