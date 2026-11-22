-- Migration 029: Add order payment deadline.

ALTER TABLE orders
    ADD COLUMN payment_due_at TIMESTAMPTZ;

-- Backfill existing orders using the original order date.
UPDATE orders
SET payment_due_at = order_date + INTERVAL '24 hours'
WHERE payment_due_at IS NULL;

-- Require a payment deadline for every order.
ALTER TABLE orders
    ALTER COLUMN payment_due_at SET NOT NULL;
