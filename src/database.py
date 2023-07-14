from typing import Optional, Union
import sys
import psycopg as pg
import environ
from datetime import date

from src.util import ROOT_DIR
from src.schema import CreateDataType, FetchByIdDataType


# CREATE A CONNECTION

env = environ.Env()
# set .env from the root dir to be read
environ.Env.read_env(str(ROOT_DIR / ".env"))


# SINGLETON CLASS.
class Database(object):
    _instance = None

    def __new__(cls):
        if Database._instance is None:
            Database._instance = super().__new__(cls)
            Database._instance.__init__()

        return Database._instance._conn

    def __init__(self) -> None:
        # It is bad practice to expose sensitive information in your code.
        self._conn = pg.connect(
            host=env.str("db_host"),
            dbname=env.str("db_name"),
            user=env.str("db_user"),
            port=env.int("db_port"),
        )


def update_data(
    book_id: int, column: str, data: Union[str, date, int]
) -> Optional[int]:
    conn = Database()
    query = (
        """
      UPDATE read.book
      SET """
        + column
        + """=%s
      WHERE id=%s RETURNING id;
   """
    )

    with conn.cursor() as cursor:
        cursor.execute(query, [data, book_id])
        updated_book_id = cursor.fetchone()[0]
        conn.commit()
        return updated_book_id


def fetch_by_id(book_id: int) -> Optional[FetchByIdDataType]:
    conn = Database()

    query = """
         SELECT 
            title,
            status,
            book_desc,
            pct_read,
            start_read_date,
            end_read_date
         FROM read.book
         WHERE id=%s;   
    """
    with conn.cursor() as cursor:
        cursor.execute(query, [book_id])
        book = cursor.fetchone()
        return book


def insert_data(data: CreateDataType) -> Optional[int]:
    # get the connection
    conn = Database()
    # define the query
    query = """
         INSERT INTO read.book(
            username,
            title,
            book_desc,
            status,
            pct_read,
            start_read_date,
            end_read_date
         ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
   """
    # create a cursor session
    with conn.cursor() as cursor:
        # use the cursor session to execute the query
        cursor.execute(query, tuple(data.values()))  # OrderedDict
        inserted_id = cursor.fetchone()[0]
        conn.commit()
        return inserted_id


def delete_data(book_id: int):
    conn = Database()
    query = """
        DELETE FROM read.book
        WHERE id = %s
        RETURNING id;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, [book_id])
        deleted_book_id = cursor.fetchone()[0]
        conn.commit()
        if deleted_book_id is not None:
            print(f"Record with id {deleted_book_id} deleted successfully.")
        else:
            print("Deletion failed!")


def truncate_table():
    conn = Database()
    query = """
        TRUNCATE TABLE read.book;
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        conn.commit()
        print("Table truncated successfully.")


def count_books_read_completely(start_date, end_date):
    query = f"""
        SELECT COUNT(*) FROM read.book
        WHERE status = 'complete' AND end_read_date >= '{start_date}' AND end_read_date <= '{end_date}';
    """
    conn = Database()
    with conn.cursor() as cursor:
        cursor.execute(query)
        count = cursor.fetchone()[0]
    print(f"Total books read completely during the period: {count}")


def count_pending_books():
    query = """
        SELECT COUNT(*) FROM read.book
        WHERE status = 'pending';
    """
    conn = Database()
    with conn.cursor() as cursor:
        cursor.execute(query)
        count = cursor.fetchone()[0]
    print(f"Total pending books: {count}")


def search_books_by_title(title):
    query = f"""
         SELECT 
            title,
            status,
            book_desc,
            pct_read,
            start_read_date,
            end_read_date
         FROM read.book
         WHERE title=%s;   
    """;
    conn = Database()
    with conn.cursor() as cursor:
        cursor.execute(query, [title])
        books = cursor.fetchall()
    if books:
        return books
    else:
        return -1


def exit_program():
    print("Exiting the program.")
    sys.exit(0)
