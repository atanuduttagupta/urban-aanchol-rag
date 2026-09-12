CREATE TABLE product_media (
    product_media_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    product_id VARCHAR(50) NOT NULL,
    media_id UUID NOT NULL,

    relationship_type VARCHAR(50) NOT NULL DEFAULT 'Product Media',

    sort_order INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT uq_product_media_relationship
        UNIQUE (product_id, media_id, relationship_type),

    CONSTRAINT fk_product_media_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_product_media_media
        FOREIGN KEY (media_id)
        REFERENCES media_assets(media_id)
        ON DELETE CASCADE
);