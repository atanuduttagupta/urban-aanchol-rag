
CREATE TABLE order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    order_id BIGINT NOT NULL
        REFERENCES orders(order_id),

    product_id VARCHAR(50) NOT NULL
        REFERENCES products(product_id),

    product_name VARCHAR(255) NOT NULL
        CHECK (BTRIM(product_name) <> ''),

    category VARCHAR(50) NOT NULL
        CHECK (BTRIM(category) <> ''),

    brand VARCHAR(100),

    quantity INTEGER NOT NULL
        CHECK (quantity > 0),

    unit_price NUMERIC(12,2) NOT NULL
        CHECK (unit_price >= 0),

    line_discount NUMERIC(12,2) NOT NULL DEFAULT 0
        CHECK (line_discount >= 0),

    line_total NUMERIC(12,2) NOT NULL,

    notes TEXT,

    attribute1 VARCHAR(255),
    attribute2 VARCHAR(255),
    attribute3 VARCHAR(255),
    attribute4 VARCHAR(255),
    attribute5 VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT order_items_discount_check
        CHECK (line_discount <= quantity * unit_price),

    CONSTRAINT order_items_total_calculation_check
        CHECK (line_total = quantity * unit_price - line_discount),

    CONSTRAINT order_items_line_total_check
        CHECK (line_total >= 0)
);

CREATE INDEX idx_order_items_order_id
    ON order_items(order_id);

CREATE INDEX idx_order_items_product_id
    ON order_items(product_id);
