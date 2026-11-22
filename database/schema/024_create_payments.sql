-- Migration 024: Create customer payments.

CREATE TABLE payments (
    payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    payment_number VARCHAR(50) NOT NULL UNIQUE,

    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),

    payment_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    amount NUMERIC(12,2) NOT NULL
        CHECK (amount > 0),

    payment_method VARCHAR(30) NOT NULL
        CHECK (payment_method IN (
            'UPI',
            'Bank Transfer',
            'Cash',
            'Other'
        )),

    payment_status VARCHAR(25) NOT NULL DEFAULT 'PendingVerification'
        CHECK (payment_status IN (
            'PendingVerification',
            'Confirmed',
            'Rejected',
            'Reversed'
        )),

    transaction_reference VARCHAR(150),

    notes TEXT,

    attribute1 VARCHAR(255),
    attribute2 VARCHAR(255),
    attribute3 VARCHAR(255),
    attribute4 VARCHAR(255),
    attribute5 VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT payments_id_customer_id_key
        UNIQUE (payment_id, customer_id)
);

CREATE INDEX idx_payments_customer_id
    ON payments(customer_id);

CREATE INDEX idx_payments_payment_date
    ON payments(payment_date);

CREATE INDEX idx_payments_payment_status
    ON payments(payment_status);
