"""Database tasks."""
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

# from pypistats.extensions import db
from pypistats.secret import postgresql


DBNAME = "pypistats"


def create_databases():
    """Create the databases for each environment."""
    env = "prod"
    url = \
        "postgresql://{username}:{password}@{host}:{port}/{dbname}".format(
            username=postgresql[env]["username"],
            password=postgresql[env]["password"],
            host=postgresql[env]["host"],
            port=postgresql[env]["port"],
            dbname=DBNAME,
        )
    engine = create_engine(url)
    connection = engine.connect()

    for env, config in postgresql.items():
        query = f"""CREATE DATABASE {config["dbname"]}"""
        try:
            connection.execute("commit")
            connection.execute(query)
            connection.execute("commit")
            print(f"Created db: {config['dbname']}.")
        except ProgrammingError:
            print(f"Database {config['dbname']} already exists.")


def get_db_connection(env="dev"):
    """Get a db connection cursor."""
    connection = psycopg2.connect(
        dbname=postgresql[env]['dbname'],
        user=postgresql[env]['username'],
        password=postgresql[env]['password'],
        host=postgresql[env]['host'],
        port=postgresql[env]['port'],
        # sslmode='require',
    )
    cursor = connection.cursor()
    return cursor


if __name__ == "__main__":
    create_databases()
