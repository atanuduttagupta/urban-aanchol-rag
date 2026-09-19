-- Day 7: Product full-text search foundation

ALTER TABLE products
ADD COLUMN search_vector tsvector;

CREATE OR REPLACE FUNCTION products_search_vector_update()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.search_vector :=
        setweight(
            to_tsvector(
                'simple',
                concat_ws(
                    ' ',
                    NEW.product_name,
                    NEW.category,
                    NEW.brand,
                    NEW.collection,
                    NEW.fabric,
                    NEW.colour,
                    NEW.secondary_colour,
                    NEW.pattern,
                    NEW.border,
                    NEW.description,
                    NEW.remarks
                )
            ),
            'A'
        );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_products_search_vector_update
BEFORE INSERT OR UPDATE OF
    product_name,
    category,
    brand,
    collection,
    fabric,
    colour,
    secondary_colour,
    pattern,
    border,
    description,
    remarks
ON products
FOR EACH ROW
EXECUTE FUNCTION products_search_vector_update();

UPDATE products
SET search_vector =
    setweight(
        to_tsvector(
            'simple',
            concat_ws(
                ' ',
                product_name,
                category,
                brand,
                collection,
                fabric,
                colour,
                secondary_colour,
                pattern,
                border,
                description,
                remarks
            )
        ),
        'A'
    );

CREATE INDEX idx_products_search_vector
ON products
USING GIN (search_vector);