CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,

    category VARCHAR(50) NOT NULL
        CHECK (category IN (
            'Saree',
            'Blouse',
            'Dupatta',
            'Jewelry',
            'Accessories',
            'Other'
        )),

    brand VARCHAR(100),
    collection VARCHAR(150),

    fabric VARCHAR(150),
    colour VARCHAR(100),
    secondary_colour VARCHAR(100),
    pattern VARCHAR(150),
    border VARCHAR(255),

    price DECIMAL(10,2)
        CHECK (price >= 0),

    availability VARCHAR(20) NOT NULL
        CHECK (availability IN (
            'Available',
            'Sold',
            'Reserved',
            'Inactive'
        )),

    description TEXT,
    product_url TEXT,
    remarks TEXT,

    additional_attributes JSONB,

    launch_date DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);