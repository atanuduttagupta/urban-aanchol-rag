-- Migration 026: Link inventory holds to registered customers.

ALTER TABLE product_holds
    ADD COLUMN customer_id BIGINT
        REFERENCES customers(customer_id);

CREATE INDEX idx_product_holds_customer_id
    ON product_holds(customer_id);
