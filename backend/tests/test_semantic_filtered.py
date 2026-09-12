from backend.app.database.connection import get_database_connection
from sentence_transformers import SentenceTransformer, util


MODEL_NAME = "all-MiniLM-L6-v2"
QUERY = "Something graceful to wear to Puja"


def load_sarees():
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
                  AND p.category = 'Saree'
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


def main():
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    products = load_sarees()
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

    ranked_products = sorted(
        zip(products, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    print()
    print(f"Query: {QUERY}")
    print()
    print("SEMANTIC RESULTS — AVAILABLE SAREES ONLY")
    print("-----------------------------------------")

    for rank, (product, score) in enumerate(
        ranked_products,
        start=1,
    ):
        print(
            f"{rank}. {product[0]} | "
            f"{product[1]} | "
            f"Score: {float(score):.4f}"
        )


if __name__ == "__main__":
    main()