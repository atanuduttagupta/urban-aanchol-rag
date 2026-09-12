from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.connection import get_database_connection
from backend.app.database.media_repository import insert_product_media


def main():
    products = load_default_catalogue()

    connection = get_database_connection()

    try:
        counts = insert_product_media(connection, products)
        connection.commit()

        print(f"Images inserted: {counts['images']}")
        print(f"Videos inserted: {counts['videos']}")
        print(f"Product-media links inserted: {counts['links']}")
        print("Product media import completed successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()