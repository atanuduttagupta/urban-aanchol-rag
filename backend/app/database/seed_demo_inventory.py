
import argparse

from backend.app.catalogue.pipeline import load_default_catalogue
from backend.app.database.connection import get_database_connection

EXPECTED_DEMO_PRODUCTS = 30


def seed_demo_inventory(apply: bool = False) -> None:
    products = load_default_catalogue()

    if len(products) != EXPECTED_DEMO_PRODUCTS:
        raise ValueError(
            f"Expected {EXPECTED_DEMO_PRODUCTS} demo products, "
            f"found {len(products)}."
        )

    excel_products = {
        product["product_id"]: product
        for product in products
    }

    if len(excel_products) != len(products):
        raise ValueError("Duplicate product IDs found in demo catalogue.")

    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT product_id, stock_quantity, availability
                FROM products
                ORDER BY product_id
                FOR UPDATE
            """)

            database_rows = cursor.fetchall()

            database_ids = {row[0] for row in database_rows}
            excel_ids = set(excel_products)

            if database_ids != excel_ids:
                raise ValueError(
                    "Database and Excel product IDs do not match. "
                    f"Missing in database: {sorted(excel_ids - database_ids)}. "
                    f"Extra in database: {sorted(database_ids - excel_ids)}."
                )

            if len(database_rows) != EXPECTED_DEMO_PRODUCTS:
                raise ValueError(
                    f"Expected {EXPECTED_DEMO_PRODUCTS} database products, "
                    f"found {len(database_rows)}."
                )

            nonzero_stock = [
                row[0] for row in database_rows if row[1] != 0
            ]

            if nonzero_stock:
                raise ValueError(
                    "Demo seeding stopped. Some products already have "
                    f"nonzero stock: {nonzero_stock}"
                )

            cursor.execute("""
                SELECT COUNT(*)
                FROM product_holds
            """)

            hold_count = cursor.fetchone()[0]

            if hold_count != 0:
                raise ValueError(
                    f"Demo seeding stopped. Found {hold_count} existing holds."
                )

            print("Demo inventory pre-check passed.")
            print(f"Products matched: {len(database_rows)}")
            print(f"Existing holds: {hold_count}")

            if not apply:
                print("\nDRY RUN: No database records were modified.")
                print("\nProposed demo inventory:")

                for product_id in sorted(excel_products):
                    product = excel_products[product_id]
                    print(
                        f"{product_id}: "
                        f"stock={product['stock_quantity']}, "
                        f"availability={product['availability']}"
                    )

                connection.rollback()
                return

            for product_id, product in excel_products.items():
                cursor.execute(
                    """
                    UPDATE products
                    SET
                        stock_quantity = %s,
                        availability = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE product_id = %s
                    """,
                    (
                        product["stock_quantity"],
                        product["availability"],
                        product_id,
                    ),
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        f"Expected one updated row for {product_id}, "
                        f"updated {cursor.rowcount}."
                    )

        connection.commit()

        print("\nDemo inventory seeded successfully.")
        print(f"Products updated: {len(products)}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed Urban Aanchol demo inventory."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply demo inventory updates. Default is dry run.",
    )

    args = parser.parse_args()

    seed_demo_inventory(apply=args.apply)


if __name__ == "__main__":
    main()
