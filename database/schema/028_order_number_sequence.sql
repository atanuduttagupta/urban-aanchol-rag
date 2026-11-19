
-- Migration 028: Create a sequence for unique order numbers.

CREATE SEQUENCE order_number_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Synchronize the sequence with existing order numbers.
-- This prevents collisions if orders already exist.

SELECT setval(
    'order_number_seq',
    COALESCE(
        (
            SELECT MAX(
                CAST(
                    SUBSTRING(order_number FROM '^UA-ORD-([0-9]+)$')
                    AS BIGINT
                )
            )
            FROM orders
            WHERE order_number ~ '^UA-ORD-[0-9]+$'
        ),
        0
    ) + 1,
    false
);
