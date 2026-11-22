CREATE TABLE customers (
    customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    full_name VARCHAR(150) NOT NULL
        CHECK (BTRIM(full_name) <> ''),

    mobile_number VARCHAR(20) NOT NULL
        CHECK (BTRIM(mobile_number) <> ''),

    whatsapp_number VARCHAR(20),
    email VARCHAR(254),

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
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_mobile_number
    ON customers(mobile_number);
