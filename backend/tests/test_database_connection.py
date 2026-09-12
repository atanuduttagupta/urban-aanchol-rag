from backend.app.database.connection import get_database_connection


def main():
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_user, version();"
            )
            database, user, version = cursor.fetchone()

            print(f"Database: {database}")
            print(f"User: {user}")
            print(f"PostgreSQL: {version.split(',')[0]}")
            print("Database connection successful.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()