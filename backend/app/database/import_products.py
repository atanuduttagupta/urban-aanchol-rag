from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.connection import get_database_connection
from backend.app.database.product_mapper import map_products_to_database
from backend.app.database.product_repository import insert_products


def main():
    products = load_default_catalogue()
    mapped_products = map_products_to_database(products)

    connection = get_database_connection()

    try:
        inserted_count = insert_products(connection, mapped_products)
        connection.commit()

        print(f"Products processed: {inserted_count}")
        print("Product import completed successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()