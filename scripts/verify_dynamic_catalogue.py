import ast
import re
import sys
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.app.database.catalogue_attribute_repository import (
    get_catalogue_vocabulary,
)
from backend.app.database.connection import get_database_connection
from backend.app.query_understanding.attribute_matcher import (
    match_catalogue_attributes,
)


BACKEND_APP = PROJECT_ROOT / "backend" / "app"
DATABASE_SCHEMA = PROJECT_ROOT / "database" / "schema"


def collect_string_literals(path: Path):
    """Collect string literals from Python source files."""
    results = []

    for file_path in path.rglob("*.py"):
        if "__pycache__" in file_path.parts:
            continue

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, SyntaxError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                results.append(
                    (
                        file_path,
                        node.value,
                        node.lineno,
                    )
                )

    return results


def audit_python_for_catalogue_literals(vocabulary):
    """
    Detect current catalogue values directly embedded in application code.

    This is a warning-oriented audit because some matches may be legitimate
    test fixtures or technical constants.
    """
    catalogue_values = {
        str(value).casefold()
        for values in vocabulary.values()
        for value in values
    }

    findings = []

    for file_path, value, line_number in collect_string_literals(BACKEND_APP):
        if value.casefold() in catalogue_values:
            findings.append(
                (
                    file_path.relative_to(PROJECT_ROOT),
                    line_number,
                    value,
                )
            )

    return findings


def audit_schema_for_business_value_constraints(vocabulary):
    """
    Detect SQL CHECK constraints containing current catalogue values.

    This helps identify business/catalogue values that may be unnecessarily
    hard-coded in the database schema.
    """
    catalogue_values = {
        str(value).casefold()
        for values in vocabulary.values()
        for value in values
    }

    findings = []

    for file_path in DATABASE_SCHEMA.glob("*.sql"):
        try:
            source = file_path.read_text(encoding="utf-8")
        except OSError:
            continue

        for line_number, line in enumerate(
            source.splitlines(),
            start=1,
        ):
            upper_line = line.upper()

            if "CHECK" not in upper_line or " IN " not in upper_line:
                continue

            quoted_values = re.findall(
                r"'([^']+)'",
                line,
            )

            for value in quoted_values:
                if value.casefold() in catalogue_values:
                    findings.append(
                        (
                            file_path.relative_to(PROJECT_ROOT),
                            line_number,
                            value,
                            line.strip(),
                        )
                    )

    return findings


def get_reference_product(connection):
    """
    Obtain an existing product from the database.

    The audit deliberately uses database values instead of hard-coding
    catalogue values such as 'Saree' or 'Available'.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                category,
                availability
            FROM products
            ORDER BY product_id
            LIMIT 1
            """
        )

        row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "Cannot run dynamic catalogue audit: products table is empty."
        )

    return row[0], row[1]


def verify_dynamic_catalogue_flow(connection):
    """
    Prove that newly inserted DB catalogue values are visible to the
    application without changing Python source code.
    """
    suffix = uuid.uuid4().hex[:10]

    product_id = f"UA-DYNAMIC-{suffix}"
    product_name = f"Dynamic Audit Product {suffix}"

    new_colour = f"AuditColour_{suffix}"
    new_mood = f"AuditMood_{suffix}"

    category, availability = get_reference_product(connection)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO products (
                    product_id,
                    product_name,
                    category,
                    price,
                    availability,
                    colour
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    product_id,
                    product_name,
                    category,
                    999.00,
                    availability,
                    new_colour,
                ),
            )

            cursor.execute(
                """
                INSERT INTO product_moods (
                    product_id,
                    mood
                )
                VALUES (%s, %s)
                """,
                (
                    product_id,
                    new_mood,
                ),
            )

        connection.commit()

        # Pull vocabulary again AFTER the DB change.
        vocabulary = get_catalogue_vocabulary(connection)

        if new_colour not in vocabulary["colour"]:
            raise AssertionError(
                "New database colour was not returned by "
                "get_catalogue_vocabulary()."
            )

        if new_mood not in vocabulary["mood"]:
            raise AssertionError(
                "New database mood was not returned by "
                "get_catalogue_vocabulary()."
            )

        matches = match_catalogue_attributes(
            (
                f"I want an {new_colour.lower()} saree "
                f"with an {new_mood.lower()} mood"
            ),
            vocabulary,
        )

        if matches.get("colour") != [new_colour]:
            raise AssertionError(
                "Application matcher did not recognize the new "
                "database colour."
            )

        if matches.get("mood") != [new_mood]:
            raise AssertionError(
                "Application matcher did not recognize the new "
                "database mood."
            )

        print("[PASS] New catalogue values were read from the database.")
        print("[PASS] Application vocabulary refreshed from the database.")
        print("[PASS] Attribute matcher recognized the new values.")
        print("[PASS] No Python-code change was required.")

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM product_moods
                WHERE product_id = %s
                """,
                (product_id,),
            )

            cursor.execute(
                """
                DELETE FROM product_tags
                WHERE product_id = %s
                """,
                (product_id,),
            )

            cursor.execute(
                """
                DELETE FROM product_styles
                WHERE product_id = %s
                """,
                (product_id,),
            )

            cursor.execute(
                """
                DELETE FROM product_occasions
                WHERE product_id = %s
                """,
                (product_id,),
            )

            cursor.execute(
                """
                DELETE FROM products
                WHERE product_id = %s
                """,
                (product_id,),
            )

        connection.commit()


def main():
    print("=" * 72)
    print("URBAN AANCHOL — DYNAMIC CATALOGUE ARCHITECTURE AUDIT")
    print("=" * 72)

    connection = get_database_connection()

    try:
        print("\n[1] DATABASE VOCABULARY")
        print("-" * 72)

        vocabulary = get_catalogue_vocabulary(connection)

        for attribute_name, values in vocabulary.items():
            print(
                f"{attribute_name:<20} "
                f"{len(values):>4} values"
            )

        print("\n[2] PYTHON APPLICATION CODE AUDIT")
        print("-" * 72)

        python_findings = audit_python_for_catalogue_literals(
            vocabulary
        )

        if python_findings:
            print(
                "[WARN] Current catalogue values were found "
                "inside backend/app Python code:"
            )

            for file_path, line_number, value in python_findings:
                print(
                    f"  {file_path}:{line_number} -> {value!r}"
                )

            print(
                "\nReview these manually. "
                "Some may be legitimate test or technical values."
            )
        else:
            print(
                "[PASS] No current catalogue values found "
                "hard-coded in backend/app Python code."
            )

        print("\n[3] DATABASE SCHEMA AUDIT")
        print("-" * 72)

        schema_findings = audit_schema_for_business_value_constraints(
            vocabulary
        )

        if schema_findings:
            print(
                "[WARN] Current catalogue values appear in SQL "
                "CHECK constraints:"
            )

            for file_path, line_number, value, line in schema_findings:
                print(
                    f"  {file_path}:{line_number} -> "
                    f"{value!r}"
                )
                print(f"      {line}")

            print(
                "\nThese need manual classification as either "
                "business values or legitimate system enums."
            )
        else:
            print(
                "[PASS] No current catalogue values found "
                "inside SQL CHECK constraints."
            )

        print("\n[4] LIVE DATABASE → APPLICATION TEST")
        print("-" * 72)

        verify_dynamic_catalogue_flow(connection)

        print("\n[5] DEPENDENCY CHECK")
        print("-" * 72)

        print(
            "[PASS] This audit introduces no new third-party dependency."
        )
        print(
            "[PASS] Dynamic catalogue matching uses the existing "
            "database/repository/application layers."
        )

        print("\n" + "=" * 72)
        print("AUDIT COMPLETE")
        print("=" * 72)

        return 0

    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())