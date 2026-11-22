CREATE TABLE orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    order_number VARCHAR(50) NOT NULL UNIQUE,

    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),

    order_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expected_delivery_date DATE,

    order_status VARCHAR(20) NOT NULL DEFAULT 'Draft'
        CHECK (order_status IN (
            'Draft',
            'Placed',
            'Confirmed',
            'Processing',
            'Completed',
            'Cancelled'
        )),

    invoice_number VARCHAR(50) UNIQUE,
    invoice_date DATE,
    invoice_issued_at TIMESTAMPTZ,

    subtotal NUMERIC(12,2) NOT NULL DEFAULT 0
        CHECK (subtotal >= 0),

    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0
        CHECK (discount_amount >= 0),

    delivery_charge NUMERIC(12,2) NOT NULL DEFAULT 0
        CHECK (delivery_charge >= 0),

    grand_total NUMERIC(12,2) NOT NULL DEFAULT 0
        CHECK (grand_total >= 0),

    currency VARCHAR(3) NOT NULL DEFAULT 'INR',

    bill_to_contact_name VARCHAR(150),
    bill_to_phone VARCHAR(20),
    bill_to_address TEXT,

    ship_to_contact_name VARCHAR(150),
    ship_to_phone VARCHAR(20),
    ship_to_address TEXT,

    notes TEXT,

    attribute1 VARCHAR(255),
    attribute2 VARCHAR(255),
    attribute3 VARCHAR(255),
    attribute4 VARCHAR(255),
    attribute5 VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT orders_discount_check
        CHECK (discount_amount <= subtotal),

    CONSTRAINT orders_total_calculation_check
        CHECK (grand_total = subtotal - discount_amount + delivery_charge),

    CONSTRAINT orders_invoice_details_check
        CHECK (
            (invoice_number IS NULL AND invoice_date IS NULL AND invoice_issued_at IS NULL)
            OR
            (invoice_number IS NOT NULL AND invoice_date IS NOT NULL AND invoice_issued_at IS NOT NULL)
        )
);

CREATE INDEX idx_orders_customer_id
    ON orders(customer_id);

CREATE INDEX idx_orders_order_date
    ON orders(order_date);

CREATE INDEX idx_orders_order_status
    ON orders(order_status);
