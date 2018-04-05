"""Get the download stats for a specific day."""
import datetime
import os
# import sys

# from google.api_core.exceptions import Conflict
from google.cloud import bigquery
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from pypistats.secret import postgresql


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "secret",
        "secret.json",
)

# Mirrors to disregard when considering downloads
MIRRORS = ("bandersnatch", "z3c.pypimirror", "Artifactory", "devpi")

# PyPI systems
SYSTEMS = ("Windows", "Linux", "Darwin")

# BigQuery definitions
DATASET_ID = "pypistats"
TABLE_ID = "pypistats"
SCHEMA = [
    bigquery.SchemaField("package", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("category_label", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("category", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("downloads", "INTEGER", mode="NULLABLE"),
]


def get_daily_download_stats(date, env="dev"):
    """Get daily download stats for pypi packages from BigQuery."""
    job_config = bigquery.QueryJobConfig()
    bq_client = bigquery.Client()

    # # Prepare a reference to the new dataset
    # dataset_ref = bq_client.dataset(DATASET_ID)
    # dataset = bigquery.Dataset(dataset_ref)
    #
    # # Create the dataset
    # try:
    #     dataset = bq_client.create_dataset(dataset)
    # except Conflict:
    #     pass
    #
    # # Prepare a reference to the table
    # table_ref = dataset_ref.table(TABLE_ID)
    # table = bigquery.Table(table_ref, schema=SCHEMA)
    #
    # # Create the table
    # try:
    #     table = bq_client.create_table(table)
    # except Conflict:
    #     pass

    local = False
    if env == "dev":
        try:
            print("Loading from csv...")
            df = pd.read_csv("ignore/sample_data.csv", index_col=0)
            print("Done.")
            # print(set(df["category_label"].values))
            # sys.exit()
            local = True
        except Exception:
            print("Loading failed.")

    if not local:
        print("Querying BigQuery...")
        # Get and perform the query, writing to destination table
        query = get_query(date)
        print("Done.")
        # job_config.destination = table_ref
        # job_config.write_disposition = "WRITE_TRUNCATE"
        query_job = bq_client.query(query, job_config=job_config)
        iterator = query_job.result()
        rows = list(iterator)

        data = []
        for row in rows:
            data.append((
                date,
                row['package'],
                row['category_label'],
                row['category'],
                row['downloads']
            ))

        df = pd.DataFrame(data, columns=[
            "date",
            "package",
            "category_label",
            "category",
            "downloads",
        ])

        df.to_csv("ignore/sample_data.csv")

    return update_db(df, env)


def update_db(df, env="dev"):
    """Update the db for the table."""
    connection = psycopg2.connect(
        dbname=postgresql[env]['dbname'],
        user=postgresql[env]['username'],
        password=postgresql[env]['password'],
        host=postgresql[env]['host'],
        port=postgresql[env]['port'],
        # sslmode='require',
    )
    cursor = connection.cursor()

    df_groups = df.groupby("category_label")

    success = {}
    for category_label, df_category in df_groups:
        table = category_label
        df_category = df_category[[
            "date",
            "package",
            "category",
            "downloads",
        ]]
        # success[table] = update_table(cursor, table, df_category, date)
        update_all_package_stats(cursor, table, date)

    update_recent_stats(cursor, date)

    return success


def update_table(cursor, table, df, date):
    """Update a table."""
    print(table)
    df = df.fillna("null")

    delete_query = \
        f"""DELETE FROM {table}
            WHERE date = '{date}'"""
    insert_query = \
        f"""INSERT INTO {table} (date, package, category, downloads)
            VALUES %s"""
    values = list(df.itertuples(index=False, name=None))
    try:
        cursor.execute(delete_query)
        execute_values(cursor, insert_query, values)
        cursor.execute("commit")
        return True
    except psycopg2.IntegrityError as e:
        cursor.execute("rollback")
        return False


def update_all_package_stats(cursor, table, date):
    """Update stats for __all__ packages."""
    print("__all__")
    aggregate_query = \
        f"""SELECT date, '__all__' AS package, category, sum(downloads) AS downloads
            FROM {table} GROUP BY date, category"""
    cursor.execute(aggregate_query, (table,))
    values = cursor.fetchall()

    delete_query = \
        f"""DELETE FROM {table}
            WHERE date = '{date}' and package = '__all__'"""
    insert_query = \
        f"""INSERT INTO {table} (date, package, category, downloads)
            VALUES %s"""
    try:
        cursor.execute(delete_query)
        execute_values(cursor, insert_query, values)
        cursor.execute("commit")
        return True
    except psycopg2.IntegrityError as e:
        cursor.execute("rollback")
        return False


def update_recent_stats(cursor, date):
    """Update daily, weekly, monthly stats for all packages."""
    print("recent")
    downloads_table = "overall"
    recent_table = "recent"

    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    date_week = date - datetime.timedelta(days=7)
    date_month = date - datetime.timedelta(days=30)

    where = {
        "day": f"date = '{str(date)}'",
        "week": f"date > '{str(date_week)}'",
        "month": f"date > '{str(date_month)}'",
    }

    success = {}
    for time, clause in where.items():
        select_query = \
            f"""SELECT package, '{time}' as category, sum(downloads) AS downloads
                FROM {downloads_table}
                WHERE category = 'without_mirrors' and {clause}
                GROUP BY package"""
        cursor.execute(select_query)
        values = cursor.fetchall()

        delete_query = \
            f"""DELETE FROM {recent_table}
                WHERE category = '{time}'"""
        insert_query = \
            f"""INSERT INTO {recent_table}
               (package, category, downloads) VALUES %s"""
        try:
            cursor.execute(delete_query)
            execute_values(cursor, insert_query, values)
            cursor.execute("commit")
            success[time] = True
        except psycopg2.IntegrityError as e:
            cursor.execute("rollback")
            success[time] = False


def get_query(date):
    """Get the query to execute against pypistats on bigquery."""
    return f"""
    WITH
      dls AS (
      SELECT
        country_code,
        file.project AS package,
        file.version AS package_version,
        file.type AS file_type,
        details.installer.name AS installer,
        details.python AS python_version,
        details.implementation.name AS python_implementation,
        details.distro.name AS distro,
        details.system.name AS system
      FROM
        `the-psf.pypi.downloads{date.replace("-", "")}` )
    SELECT
      package,
      'python_major' AS category_label,
      cast(SPLIT(python_version, '.')[
    OFFSET
      (0)] as string) AS category,
      COUNT(*) AS downloads
    FROM
      dls
    WHERE
      installer NOT IN {str(MIRRORS)}
    GROUP BY
      package,
      category
    UNION ALL
    SELECT
      package,
      'python_minor' AS category_label,
      cast(CONCAT(SPLIT(python_version, '.')[
      OFFSET
        (0)],'.',SPLIT(python_version, '.')[
      OFFSET
        (1)]) as string) AS category,
      COUNT(*) AS downloads
    FROM
      dls
    WHERE
      installer NOT IN {str(MIRRORS)}
    GROUP BY
      package,
      category
    UNION ALL
    SELECT
      package,
      'overall' AS category_label,
      'with_mirrors' AS category,
      COUNT(*) AS downloads
    FROM
      dls
    GROUP BY
      package,
      category
    UNION ALL
    SELECT
      package,
      'overall' AS category_label,
      'without_mirrors' AS category,
      COUNT(*) AS downloads
    FROM
      dls
    WHERE
      installer NOT IN {str(MIRRORS)}
    GROUP BY
      package,
      category
    UNION ALL
    SELECT
      package,
      'system' AS category_label,
      CASE
        WHEN system NOT IN {str(SYSTEMS)} THEN 'other'
        ELSE system
      END AS category,
      COUNT(*) AS downloads
    FROM
      dls
    WHERE
      installer NOT IN {str(MIRRORS)}
    GROUP BY
      package,
      category
    """


if __name__ == "__main__":
    date = "2018-02-08"
    print(get_daily_download_stats(date))
