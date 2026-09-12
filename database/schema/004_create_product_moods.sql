CREATE TABLE product_moods (
    product_id VARCHAR(50) NOT NULL,
    mood VARCHAR(100) NOT NULL,

    PRIMARY KEY (product_id, mood),

    CONSTRAINT fk_product_moods_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);