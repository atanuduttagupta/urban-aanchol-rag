CREATE TABLE product_occasions (
    product_id VARCHAR(50) NOT NULL,
    occasion VARCHAR(100) NOT NULL,

    PRIMARY KEY (product_id, occasion),

    CONSTRAINT fk_product_occasions_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);