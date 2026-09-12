CREATE TABLE product_styles (
    product_id VARCHAR(50) NOT NULL,
    style VARCHAR(100) NOT NULL,

    PRIMARY KEY (product_id, style),

    CONSTRAINT fk_product_styles_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);