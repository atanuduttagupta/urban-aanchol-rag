-- Migration 027: Link converted inventory holds to orders.

ALTER TABLE product_holds
    ADD COLUMN order_id BIGINT
        REFERENCES orders(order_id);

CREATE INDEX idx_product_holds_order_id
    ON product_holds(order_id);
