
-- Migration 030: Create order idempotency records.
--
-- Prevents duplicate order creation when a customer retries
-- the same order submission.

CREATE TABLE order_idempotency (
    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),

    idempotency_key UUID NOT NULL,

    request_hash CHAR(64) NOT NULL
        CHECK (request_hash ~ '^[0-9a-f]{64}$'),

    order_id BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_order_idempotency
        PRIMARY KEY (customer_id, idempotency_key),

    CONSTRAINT uq_order_idempotency_order_id
        UNIQUE (order_id),

    CONSTRAINT fk_order_idempotency_order_customer
        FOREIGN KEY (order_id, customer_id)
        REFERENCES orders(order_id, customer_id)
);
