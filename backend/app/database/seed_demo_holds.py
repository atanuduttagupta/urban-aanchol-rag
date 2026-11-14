
import argparse

from backend.app.database.connection import get_database_connection


DEMO_HOLDS = [
    {
        "product_id": "UA-0016",
        "customer_reference": "DEMO-CUSTOMER-001",
        "quantity": 2,
        "notes": "Demo reservation for inventory management testing.",
    },
    {
        "product_id": "UA-0017",
        "customer_reference": "DEMO-CUSTOMER-002",
        "quantity": 1,
        "notes": "Demo reservation for inventory management testing.",
    },
]

TEST_PRODUCT = {
    "product_id": "UA-0018",
    "expected_stock": 0,
    "expected_availability": "Reserved",
}


def seed_demo_holds(apply: bool = False) -> None:
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            product_ids = [
                hold["product_id"] for hold in DEMO_HOLDS
            ] + [TEST_PRODUCT["product_id"]]

            cursor.execute(
                """
                SELECT product_id, stock_quantity, availability
                FROM products
                WHERE product_id IN (%s, %s, %s)
                ORDER BY product_id
                FOR UPDATE
                """,
                tuple(product_ids),
            )

            rows = cursor.fetchall()
            products = {
                row[0]: {
                    "stock_quantity": row[1],
                    "availability": row[2],
                }
                for row in rows
            }

            if set(products) != set(product_ids):
                raise ValueError(
                    "Expected demo products are missing from the database."
                )

            cursor.execute(
                "SELECT COUNT(*) FROM product_holds"
            )
            existing_holds = cursor.fetchone()[0]

            if existing_holds != 0:
                raise ValueError(
                    f"Expected an empty product_holds table, "
                    f"found {existing_holds} records. "
                    "Stopping to prevent duplicate demo holds."
                )

            for hold in DEMO_HOLDS:
                product = products[hold["product_id"]]
                stock = product["stock_quantity"]

                if stock < hold["quantity"]:
                    raise ValueError(
                        f"Insufficient stock for {hold['product_id']}: "
                        f"stock={stock}, requested hold={hold['quantity']}."
                    )

                if product["availability"] != "Reserved":
                    raise ValueError(
                        f"{hold['product_id']} must have Reserved status."
                    )

            test_product = products[TEST_PRODUCT["product_id"]]

            if (
                test_product["stock_quantity"]
                != TEST_PRODUCT["expected_stock"]
                or test_product["availability"]
                != TEST_PRODUCT["expected_availability"]
            ):
                raise ValueError(
                    "UA-0018 test scenario has changed unexpectedly. "
                    f"Found stock={test_product['stock_quantity']}, "
                    f"availability={test_product['availability']}."
                )

            print("Demo hold pre-check passed.")
            print("Existing hold records: 0")
            print("\nProposed demo holds:")

            for hold in DEMO_HOLDS:
                stock = products[hold["product_id"]]["stock_quantity"]
                available = stock - hold["quantity"]

                print(
                    f"{hold['product_id']}: "
                    f"hold={hold['quantity']}, "
                    f"stock={stock}, "
                    f"available={available}"
                )

            print(
                "\nUA-0018: "
                f"stock={test_product['stock_quantity']}, "
                f"availability={test_product['availability']}, "
                "no hold will be created."
            )

            if not apply:
                print("\nDRY RUN: No database records were modified.")
                connection.rollback()
                return

            inserted = []

            for hold in DEMO_HOLDS:
                cursor.execute(
                    """
                    INSERT INTO product_holds (
                        product_id,
                        customer_reference,
                        quantity,
                        status,
                        notes
                    )
                    VALUES (%s, %s, %s, 'Active', %s)
                    RETURNING hold_id
                    """,
                    (
                        hold["product_id"],
                        hold["customer_reference"],
                        hold["quantity"],
                        hold["notes"],
                    ),
                )

                hold_id = cursor.fetchone()[0]
                inserted.append((hold["product_id"], hold_id))

        connection.commit()

        print("\nDemo holds created successfully.")

        for product_id, hold_id in inserted:
            print(f"{product_id}: hold_id={hold_id}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed Urban Aanchol demo product holds."
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create demo holds. Default is dry run.",
    )

    args = parser.parse_args()

    seed_demo_holds(apply=args.apply)


if __name__ == "__main__":
    main()
