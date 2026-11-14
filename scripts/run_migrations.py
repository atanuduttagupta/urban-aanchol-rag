import argparse
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = PROJECT_ROOT / "database" / "schema"

MIGRATION_PATTERN = re.compile(r"^(\d{3})_(.+)\.sql$")

BASELINE_VERSION = 17
ADVISORY_LOCK_ID = 180018
MIGRATION_TABLE = "schema_migrations"


def discover_migrations() -> list[tuple[int, Path]]:
    """Discover and validate numbered SQL migration files."""

    migrations = []
    versions = set()

    for path in SCHEMA_DIR.glob("*.sql"):
        match = MIGRATION_PATTERN.match(path.name)

        if not match:
            raise ValueError(f"Invalid migration filename: {path.name}")

        version = int(match.group(1))

        if version in versions:
            raise ValueError(f"Duplicate migration version: {version}")

        versions.add(version)
        migrations.append((version, path))

    migrations.sort(key=lambda item: item[0])

    expected_versions = list(range(1, len(migrations) + 1))
    actual_versions = [version for version, _ in migrations]

    if actual_versions != expected_versions:
        raise ValueError(
            "Migration sequence contains missing versions. "
            f"Found: {actual_versions}"
        )

    return migrations


def create_migration_table(cur) -> None:
    """Create migration history table if it does not exist."""

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(20) PRIMARY KEY,
            description VARCHAR(255) NOT NULL,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)


def get_applied_migrations(cur) -> dict[str, str]:
    """Return applied migration versions and descriptions."""

    cur.execute("""
        SELECT version, description
        FROM schema_migrations
        ORDER BY version;
    """)

    return {
        version: description
        for version, description in cur.fetchall()
    }


def acquire_lock(cur) -> None:
    """Prevent concurrent migration operations."""

    cur.execute(
        "SELECT pg_advisory_xact_lock(%s);",
        (ADVISORY_LOCK_ID,),
    )



def verify_legacy_schema(cur) -> None:
    """Verify essential legacy schema objects before registering baseline."""

    required_tables = {
        "products",
        "product_occasions",
        "product_styles",
        "product_moods",
        "product_tags",
        "media_assets",
        "product_media",
        "knowledge_documents",
        "knowledge_chunks",
        "knowledge_entities",
        "knowledge_entity_relations",
        "knowledge_document_entities",
        "knowledge_chunk_entities",
        "product_embeddings",
        "knowledge_chunk_embeddings",
    }

    required_indexes = {
        "idx_products_category",
        "idx_products_fabric",
        "idx_products_colour",
        "idx_products_brand",
        "idx_products_collection",
        "idx_products_availability",
        "idx_products_price",
        "idx_product_occasions_occasion",
        "idx_product_styles_style",
        "idx_product_moods_mood",
        "idx_product_tags_tag",
        "idx_media_assets_type_status",
        "idx_product_media_product",
        "idx_product_media_media",
        "idx_knowledge_documents_type_status",
        "idx_knowledge_documents_status_priority",
        "idx_knowledge_chunks_document",
        "idx_knowledge_entities_type",
        "idx_knowledge_entities_name",
        "idx_entity_relations_source",
        "idx_entity_relations_target",
        "idx_entity_relations_type",
        "idx_document_entities_document",
        "idx_document_entities_entity",
        "idx_document_entities_relationship",
        "idx_chunk_entities_entity",
        "idx_products_search_vector",
    }

    # 1. Verify legacy tables.
    cur.execute("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public';
    """)
    existing_tables = {row[0] for row in cur.fetchall()}

    missing_tables = required_tables - existing_tables

    if missing_tables:
        raise RuntimeError(
            f"Baseline refused: missing tables: {sorted(missing_tables)}"
        )

    # 2. Verify administrative availability constraint.
    cur.execute("""
        SELECT pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'public.products'::regclass
          AND conname = 'products_availability_check';
    """)
    constraint = cur.fetchone()

    if constraint is None:
        raise RuntimeError(
            "Baseline refused: products availability constraint is missing."
        )

    expected_statuses = {
        "Available",
        "Sold",
        "Reserved",
        "Inactive",
    }

    actual_statuses = set(
        re.findall(r"'([^']+)'", constraint[0])
    )

    if actual_statuses != expected_statuses:
        raise RuntimeError(
            "Baseline refused: unexpected availability constraint values."
        )

    # 3. Verify all indexes from migrations 014 and 017.
    cur.execute("""
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public';
    """)
    existing_indexes = {row[0] for row in cur.fetchall()}

    missing_indexes = required_indexes - existing_indexes

    if missing_indexes:
        raise RuntimeError(
            f"Baseline refused: missing indexes: {sorted(missing_indexes)}"
        )

    # 4. Verify the search_vector column.
    cur.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'products'
              AND column_name = 'search_vector'
              AND data_type = 'tsvector'
        );
    """)

    if not cur.fetchone()[0]:
        raise RuntimeError(
            "Baseline refused: products.search_vector column is missing."
        )

    # 5. Verify full-text search function and trigger.
    cur.execute("""
        SELECT
            to_regprocedure('public.products_search_vector_update()'),
            EXISTS (
                SELECT 1
                FROM pg_trigger
                WHERE tgrelid = 'public.products'::regclass
                  AND tgname = 'trg_products_search_vector_update'
                  AND NOT tgisinternal
            );
    """)

    search_function, search_trigger = cur.fetchone()

    if not search_function or not search_trigger:
        raise RuntimeError(
            "Baseline refused: full-text search function "
            "or trigger is missing."
        )


def baseline_database() -> None:
    """Register the explicitly verified legacy database baseline."""

    with get_database_connection() as conn:
        with conn.cursor() as cur:
            acquire_lock(cur)

            # 1. Verify the existing legacy database schema.
            verify_legacy_schema(cur)
            print("Legacy schema verification passed.")

            # 2. Verify that every product has a search vector.
            cur.execute("""
                SELECT
                    COUNT(*),
                    COUNT(search_vector)
                FROM products;
            """)

            total, populated = cur.fetchone()

            if total != populated:
                raise RuntimeError(
                    "Baseline refused: product search vectors "
                    "are incomplete."
                )

            # 3. Verify that existing search vectors are correct.
            cur.execute("""
                SELECT COUNT(*)
                FROM products
                WHERE search_vector IS DISTINCT FROM
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
            """)

            if cur.fetchone()[0] != 0:
                raise RuntimeError(
                    "Baseline refused: product search vectors "
                    "are inconsistent."
                )

            print("Product search-vector verification passed.")

            # 4. Create migration history table.
            create_migration_table(cur)

            applied = get_applied_migrations(cur)

            if applied:
                raise RuntimeError(
                    "Baseline refused: migration history is not empty."
                )

            # 5. Register the verified legacy baseline.
            cur.execute("""
                INSERT INTO schema_migrations (version, description)
                VALUES (%s, %s);
            """, (
                "017",
                "Verified legacy database baseline (migrations 001-017)",
            ))

            print(
                "Baseline 017 registered. "
                "The existing database was not otherwise modified."
            )


def show_status() -> None:
    """Display migration history."""

    with get_database_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT to_regclass('public.schema_migrations');
            """)

            if cur.fetchone()[0] is None:
                print("Migration history table does not exist.")
                return

            applied = get_applied_migrations(cur)

            print("\nApplied migrations:")

            if not applied:
                print("No migration records found.")
                return

            for version, description in applied.items():
                print(f"{version}: {description}")


def migrate() -> None:
    """Execute pending migrations, recording each transactionally."""

    migrations = discover_migrations()
    available_versions = {
        f"{version:03d}" for version, _ in migrations
    }

    with get_database_connection() as conn:
        with conn.cursor() as cur:
            acquire_lock(cur)

            cur.execute("""
                SELECT to_regclass('public.schema_migrations');
            """)

            if cur.fetchone()[0] is None:
                raise RuntimeError(
                    "Migration history is missing. "
                    "Register the verified baseline first."
                )

            applied = get_applied_migrations(cur)

            # 1. Require the consolidated legacy baseline.
            if "017" not in applied:
                raise RuntimeError(
                    "Verified baseline 017 is missing. "
                    "Run --baseline 17 first."
                )

            # 2. Reject individual legacy migration records.
            unexpected_legacy = {
                version
                for version in applied
                if version.isdigit()
                and 1 <= int(version) < BASELINE_VERSION
            }

            if unexpected_legacy:
                raise RuntimeError(
                    "Unexpected individual legacy migration records: "
                    f"{sorted(unexpected_legacy)}. "
                    "Baseline 017 must represent migrations 001-017."
                )

            # 3. Reject records that do not match available migrations.
            unknown_versions = set(applied) - available_versions

            if unknown_versions:
                raise RuntimeError(
                    "Migration history contains unknown versions: "
                    f"{sorted(unknown_versions)}"
                )

            # 4. Validate migration descriptions.
            for version, path in migrations:
                version_text = f"{version:03d}"

                if version_text in applied:
                    expected_description = path.stem[4:]

                    if version_text == "017":
                        expected_description = (
                            "Verified legacy database baseline "
                            "(migrations 001-017)"
                        )

                    if applied[version_text] != expected_description:
                        raise RuntimeError(
                            f"Migration history description mismatch "
                            f"for version {version_text}."
                        )

            # 5. Apply pending migrations after the baseline.
            for version, path in migrations:
                version_text = f"{version:03d}"

                if version_text in applied:
                    print(
                        f"Skipping already recorded migration "
                        f"{version_text}"
                    )
                    continue

                if version <= BASELINE_VERSION:
                    print(
                        f"Skipping migration {version_text}: "
                        "covered by verified baseline 017"
                    )
                    continue

                sql = path.read_text(encoding="utf-8-sig")

                if re.search(
                    r"^\s*(BEGIN|COMMIT)\s*;",
                    sql,
                    re.IGNORECASE | re.MULTILINE,
                ):
                    raise RuntimeError(
                        f"Migration {version_text} contains explicit "
                        "transaction control. Remove it; the runner "
                        "manages transactions."
                    )

                print(
                    f"Applying migration {version_text}: {path.name}"
                )

                cur.execute(sql)

                cur.execute("""
                    INSERT INTO schema_migrations (version, description)
                    VALUES (%s, %s);
                """, (
                    version_text,
                    path.stem[4:],
                ))

                applied[version_text] = path.stem[4:]

                print(f"Migration {version_text} completed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Urban Aanchol database migration runner"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--dry-run",
        action="store_true",
        help="List migrations without database changes",
    )

    group.add_argument(
        "--baseline",
        type=int,
        choices=[BASELINE_VERSION],
        help="Register the verified legacy database baseline",
    )

    group.add_argument(
        "--migrate",
        action="store_true",
        help="Execute pending migrations",
    )

    group.add_argument(
        "--status",
        action="store_true",
        help="Show recorded migration history",
    )

    args = parser.parse_args()

    if args.dry_run:
        migrations = discover_migrations()

        print(f"Migration directory: {SCHEMA_DIR}")
        print(f"Discovered migrations: {len(migrations)}")

        for version, path in migrations:
            print(f"{version:03d} - {path.name}")

        print("\nDry run completed. No database changes made.")

    elif args.baseline is not None:
        baseline_database()

    elif args.migrate:
        migrate()

    elif args.status:
        show_status()


def get_database_connection():
    """Import the database connection lazily."""

    import sys

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from backend.app.database.connection import (
        get_database_connection as connect,
    )

    return connect()

if __name__ == "__main__":
    main()
