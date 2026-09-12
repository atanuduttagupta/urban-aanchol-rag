from backend.app.database.connection import get_database_connection
from sentence_transformers import SentenceTransformer, util


MODEL_NAME = "all-MiniLM-L6-v2"
QUERY = "Something graceful to wear to Puja"


def load_products():
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    p.product_id,
                    p.product_name,
                    p.category,
                    p.fabric,
                    p.colour,
                    p.description,
                    COALESCE(
                        string_agg(DISTINCT po.occasion, ', '),
                        ''
                    ) AS occasions,
                    COALESCE(
                        string_agg(DISTINCT ps.style, ', '),
                        ''
                    ) AS styles,
                    COALESCE(
                        string_agg(DISTINCT pm.mood, ', '),
                        ''
                    ) AS moods
                FROM products p
                LEFT JOIN product_occasions po
                    ON po.product_id = p.product_id
                LEFT JOIN product_styles ps
                    ON ps.product_id = p.product_id
                LEFT JOIN product_moods pm
                    ON pm.product_id = p.product_id
                WHERE p.availability = 'Available'
                GROUP BY
                    p.product_id,
                    p.product_name,
                    p.category,
                    p.fabric,
                    p.colour,
                    p.description
                ORDER BY p.product_id;
                """
            )

            return cursor.fetchall()

    finally:
        connection.close()


def build_product_text(product):
    (
        product_id,
        product_name,
        category,
        fabric,
        colour,
        description,
        occasions,
        styles,
        moods,
    ) = product

    return (
        f"{product_name}. "
        f"Category: {category}. "
        f"Fabric: {fabric}. "
        f"Colour: {colour}. "
        f"Occasions: {occasions}. "
        f"Styles: {styles}. "
        f"Moods: {moods}. "
        f"{description or ''}"
    )


def keyword_search():
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    product_id,
                    product_name,
                    price
                FROM products
                WHERE availability = 'Available'
                  AND to_tsvector(
                        'simple',
                        coalesce(product_name, '') || ' ' ||
                        coalesce(description, '')
                      )
                      @@ plainto_tsquery('simple', 'graceful Puja')
                ORDER BY price;
                """
            )

            return cursor.fetchall()

    finally:
        connection.close()


def semantic_search(products):
    model = SentenceTransformer(MODEL_NAME)

    product_texts = [
        build_product_text(product)
        for product in products
    ]

    query_embedding = model.encode(
        QUERY,
        convert_to_tensor=True,
    )

    product_embeddings = model.encode(
        product_texts,
        convert_to_tensor=True,
    )

    scores = util.cos_sim(
        query_embedding,
        product_embeddings,
    )[0]

    ranked = sorted(
        zip(products, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    return ranked


def main():
    products = load_products()
    keyword_results = keyword_search()
    semantic_results = semantic_search(products)

    print()
    print(f"Query: {QUERY}")

    print()
    print("KEYWORD / FULL-TEXT RESULTS")
    print("============================")

    if keyword_results:
        for product_id, product_name, price in keyword_results:
            print(
                f"{product_id} | "
                f"{product_name} | "
                f"₹{price}"
            )
    else:
        print("No keyword matches found.")

    print()
    print("SEMANTIC RESULTS")
    print("================")

    for rank, (product, score) in enumerate(
        semantic_results,
        start=1,
    ):
        print(
            f"{rank}. {product[0]} | "
            f"{product[1]} | "
            f"Score: {float(score):.4f}"
        )


if __name__ == "__main__":
    main()