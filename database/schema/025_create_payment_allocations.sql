-- Migration 025: Create payment allocations.

-- Supporting composite key to ensure allocations reference
-- orders belonging to the same customer as the payment.

ALTER TABLE orders
    ADD CONSTRAINT orders_id_customer_id_key
    UNIQUE (order_id, customer_id);


CREATE TABLE payment_allocations (
    allocation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    payment_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,

    allocated_amount NUMERIC(12,2) NOT NULL
        CHECK (allocated_amount > 0),

    allocation_status VARCHAR(15) NOT NULL DEFAULT 'Active'
        CHECK (allocation_status IN ('Active', 'Reversed')),

    allocated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    notes TEXT,

    attribute1 VARCHAR(255),
    attribute2 VARCHAR(255),
    attribute3 VARCHAR(255),
    attribute4 VARCHAR(255),
    attribute5 VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT payment_allocations_payment_customer_fkey
        FOREIGN KEY (payment_id, customer_id)
        REFERENCES payments(payment_id, customer_id),

    CONSTRAINT payment_allocations_order_customer_fkey
        FOREIGN KEY (order_id, customer_id)
        REFERENCES orders(order_id, customer_id)
);

CREATE INDEX idx_payment_allocations_payment_id
    ON payment_allocations(payment_id);

CREATE INDEX idx_payment_allocations_order_id
    ON payment_allocations(order_id);

CREATE INDEX idx_payment_allocations_customer_id
    ON payment_allocations(customer_id);

CREATE INDEX idx_payment_allocations_status
    ON payment_allocations(allocation_status);
