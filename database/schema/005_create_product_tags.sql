CREATE TABLE product_tags (
    product_id VARCHAR(50) NOT NULL,
    tag VARCHAR(100) NOT NULL,

    PRIMARY KEY (product_id, tag),

    CONSTRAINT fk_product_tags_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);