from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from backend.app.database.connection import get_database_connection
from backend.app.orders.order_repository import PostgresOrderRepository


class RollbackTestTransaction(Exception):
    pass


@pytest.fixture
def isolated_repository():
    connection = get_database_connection()

    try:
        try:
            with connection.transaction():
                repository = PostgresOrderRepository(connection)
                yield repository, connection

                # Roll back all test activity.
                raise RollbackTestTransaction()
        except RollbackTestTransaction:
            pass
    finally:
        connection.close()


def test_get_products_for_order_retrieves_real_database_products(
    isolated_repository,
):
    repository, connection = isolated_repository

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                product_id,
                product_name,
                category,
                brand,
                price,
                availability,
                stock_quantity
            FROM products
            WHERE product_id = 'UA-0001'
            """
        )
        expected = cursor.fetchone()

    assert expected is not None

    result = repository.get_products_for_order(("UA-0001",))

    assert "UA-0001" in result

    product = result["UA-0001"]

    assert product.product_id == expected[0]
    assert product.product_name == expected[1]
    assert product.category == expected[2]
    assert product.brand == expected[3]
    assert product.price == expected[4]
    assert product.availability == expected[5]
    assert product.stock_quantity == expected[6]


def test_get_products_for_order_omits_unknown_product(
    isolated_repository,
):
    repository, _ = isolated_repository

    result = repository.get_products_for_order(("UA-0001", "UA-NONEXISTENT-TEST"))

    assert "UA-0001" in result
    assert "UA-NONEXISTENT-TEST" not in result


def test_concurrent_product_locks_use_consistent_order():
    setup_connection = get_database_connection()

    try:
        with setup_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT product_id
                FROM products
                ORDER BY product_id
                LIMIT 2
                """
            )
            rows = cursor.fetchall()

        assert len(rows) == 2
        product_ids = tuple(row[0] for row in rows)

    finally:
        setup_connection.close()

    barrier = Barrier(2)

    def lock_products(requested_ids):
        connection = get_database_connection()

        try:
            with connection.transaction():
                repository = PostgresOrderRepository(connection)

                barrier.wait(timeout=10)

                result = repository.get_products_for_order(requested_ids)

                return result

        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(lock_products, product_ids)
        future_b = executor.submit(
            lock_products,
            tuple(reversed(product_ids)),
        )

        result_a = future_a.result(timeout=20)
        result_b = future_b.result(timeout=20)

    assert set(result_a) == set(product_ids)
    assert set(result_b) == set(product_ids)
