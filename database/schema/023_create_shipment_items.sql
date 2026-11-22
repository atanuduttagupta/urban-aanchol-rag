-- Add composite unique keys for shipment-item relationship validation.

ALTER TABLE shipments
    ADD CONSTRAINT shipments_id_order_id_key
    UNIQUE (shipment_id, order_id);

ALTER TABLE order_items
    ADD CONSTRAINT order_items_id_order_id_key
    UNIQUE (order_item_id, order_id);


-- Create shipment items.

CREATE TABLE shipment_items (
    shipment_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    shipment_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    order_item_id BIGINT NOT NULL,

    quantity INTEGER NOT NULL
        CHECK (quantity > 0),

    notes TEXT,

    attribute1 VARCHAR(255),
    attribute2 VARCHAR(255),
    attribute3 VARCHAR(255),
    attribute4 VARCHAR(255),
    attribute5 VARCHAR(255),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT shipment_items_shipment_order_fkey
        FOREIGN KEY (shipment_id, order_id)
        REFERENCES shipments(shipment_id, order_id),

    CONSTRAINT shipment_items_order_item_order_fkey
        FOREIGN KEY (order_item_id, order_id)
        REFERENCES order_items(order_item_id, order_id),

    CONSTRAINT shipment_items_shipment_order_item_key
        UNIQUE (shipment_id, order_item_id)
);

CREATE INDEX idx_shipment_items_order_item_id
    ON shipment_items(order_item_id);
