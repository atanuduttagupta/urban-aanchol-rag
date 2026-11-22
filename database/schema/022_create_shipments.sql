CREATE TABLE shipments (
    shipment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    order_id BIGINT NOT NULL
        REFERENCES orders(order_id),

    shipment_number VARCHAR(50) NOT NULL UNIQUE,

    shipment_date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    shipment_status VARCHAR(20) NOT NULL DEFAULT 'Planned'
        CHECK (shipment_status IN (
            'Planned',
            'Ready',
            'Dispatched',
            'In Transit',
            'Delivered',
            'Failed',
            'Returned',
            'Cancelled'
        )),

    CONSTRAINT shipments_delivery_timestamp_check
    CHECK (
        delivered_at IS NULL
        OR dispatched_at IS NOT NULL
    ),

    courier_name VARCHAR(100),
    tracking_number VARCHAR(100),

    recipient_name VARCHAR(150),
    recipient_phone VARCHAR(20),
    delivery_address TEXT,

    dispatched_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,

    notes TEXT,

    attribute1 VARCHAR(255),
    attribute2 VARCHAR(255),
    attribute3 VARCHAR(255),
    attribute4 VARCHAR(255),
    attribute5 VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shipments_order_id
    ON shipments(order_id);

CREATE INDEX idx_shipments_status
    ON shipments(shipment_status);

CREATE INDEX idx_shipments_tracking_number
    ON shipments(tracking_number);
