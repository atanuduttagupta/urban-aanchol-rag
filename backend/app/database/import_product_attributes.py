from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.connection import get_database_connection
from backend.app.database.product_attributes_repository import (
    insert_product_attributes,
)


def main():
    products = load_default_catalogue()

    connection = get_database_connection()

    try:
        counts = insert_product_attributes(connection, products)
        connection.commit()

        print(f"Occasions inserted: {counts['occasions']}")
        print(f"Styles inserted: {counts['styles']}")
        print(f"Moods inserted: {counts['moods']}")
        print(f"Tags inserted: {counts['tags']}")
        print("Product attribute import completed successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()