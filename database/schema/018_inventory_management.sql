
-- Urban Aanchol
-- Migration 018: Inventory Management

-- 1. Add physical stock quantity.
-- Existing products start with zero stock.
ALTER TABLE products
ADD COLUMN stock_quantity INTEGER NOT NULL DEFAULT 0
CONSTRAINT products_stock_quantity_check
CHECK (stock_quantity >= 0);


-- 2. Expand administrative availability statuses.
ALTER TABLE products
DROP CONSTRAINT products_availability_check;

ALTER TABLE products
ADD CONSTRAINT products_availability_check
CHECK (
    availability IN (
        'Planned',
        'Coming Soon',
        'Available',
        'Reserved',
        'Sold',
        'Inactive',
        'Discontinued'
    )
);


-- 3. Create customer hold records.
CREATE TABLE product_holds (
    hold_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    product_id VARCHAR(50) NOT NULL
        REFERENCES products(product_id),

    customer_reference VARCHAR(100),

    quantity INTEGER NOT NULL
        CHECK (quantity > 0),

    status VARCHAR(20) NOT NULL DEFAULT 'Active'
        CHECK (
            status IN ('Active', 'Released', 'Converted')
        ),

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 4. Index active holds for inventory calculations.
CREATE INDEX idx_product_holds_active
ON product_holds(product_id)
WHERE status = 'Active';
