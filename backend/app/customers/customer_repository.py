from psycopg import Connection, Cursor

from backend.app.customers.models import Customer

CUSTOMER_COLUMNS = """
    customer_id,
    full_name,
    mobile_number,
    whatsapp_number,
    email,
    bill_to_contact_name,
    bill_to_phone,
    bill_to_address,
    ship_to_contact_name,
    ship_to_phone,
    ship_to_address,
    notes,
    attribute1,
    attribute2,
    attribute3,
    attribute4,
    attribute5,
    created_at,
    updated_at
"""

CUSTOMER_DATA_FIELDS = (
    "full_name",
    "mobile_number",
    "whatsapp_number",
    "email",
    "bill_to_contact_name",
    "bill_to_phone",
    "bill_to_address",
    "ship_to_contact_name",
    "ship_to_phone",
    "ship_to_address",
    "notes",
    "attribute1",
    "attribute2",
    "attribute3",
    "attribute4",
    "attribute5",
)


def customer_from_row(row: tuple) -> Customer:
    return Customer(*row)


class PostgresCustomerRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create_customer(
        self,
        customer_data: dict[str, str | None],
    ) -> Customer:
        columns = ", ".join(CUSTOMER_DATA_FIELDS)
        placeholders = ", ".join(["%s"] * len(CUSTOMER_DATA_FIELDS))

        values = tuple(customer_data.get(field) for field in CUSTOMER_DATA_FIELDS)

        sql = f"""
            INSERT INTO customers ({columns})
            VALUES ({placeholders})
            RETURNING {CUSTOMER_COLUMNS}
        """

        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                cursor.execute(sql, values)
                row = cursor.fetchone()

        return customer_from_row(row)

    def get_customer_for_order(
        self,
        cursor: Cursor,
        customer_id: int,
    ) -> Customer | None:
        """
        Retrieve and lock a customer row for order creation.

        The caller owns the cursor and database transaction.
        FOR SHARE prevents concurrent customer updates until
        the caller's transaction completes.
        """

        sql = f"""
            SELECT {CUSTOMER_COLUMNS}
            FROM customers
            WHERE customer_id = %s
            FOR SHARE
        """

        cursor.execute(sql, (customer_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return customer_from_row(row)

    def get_customer(self, customer_id: int) -> Customer | None:
        sql = f"""
            SELECT {CUSTOMER_COLUMNS}
            FROM customers
            WHERE customer_id = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(sql, (customer_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return customer_from_row(row)

    def list_customers(
        self,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Customer]:
        sql = f"""
            SELECT {CUSTOMER_COLUMNS}
            FROM customers
        """

        params: list = []

        if search:
            sql += """
                WHERE
                    full_name ILIKE %s
                    OR mobile_number ILIKE %s
                    OR whatsapp_number ILIKE %s
                    OR email ILIKE %s
            """
            search_pattern = f"%{search}%"
            params.extend([search_pattern] * 4)

        sql += """
            ORDER BY created_at DESC, customer_id DESC
            LIMIT %s OFFSET %s
        """

        params.extend([limit, offset])

        with self.connection.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

        return [customer_from_row(row) for row in rows]

    def update_customer(
        self,
        customer_id: int,
        updates: dict[str, str | None],
    ) -> Customer | None:
        allowed_fields = set(CUSTOMER_DATA_FIELDS)
        invalid_fields = set(updates) - allowed_fields

        if invalid_fields:
            raise ValueError("Invalid customer update fields.")

        if not updates:
            return self.get_customer(customer_id)

        assignments = ", ".join(f"{field} = %s" for field in updates)

        values = list(updates.values())
        values.append(customer_id)

        sql = f"""
            UPDATE customers
            SET
                {assignments},
                updated_at = CURRENT_TIMESTAMP
            WHERE customer_id = %s
            RETURNING {CUSTOMER_COLUMNS}
        """

        with self.connection.transaction():
            with self.connection.cursor() as cursor:
                cursor.execute(sql, tuple(values))
                row = cursor.fetchone()

        if row is None:
            return None

        return customer_from_row(row)
