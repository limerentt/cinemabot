import os
from typing import Dict, List

import sqlite3


DB_FILE = "db/cinemabot.db"


def _init_db():
    with open("backend/createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


if not os.path.exists(DB_FILE):
    conn = sqlite3.connect(DB_FILE, isolation_level=None)
    cursor = conn.cursor()
    _init_db()
else:
    conn = sqlite3.connect(DB_FILE, isolation_level=None)
    cursor = conn.cursor()


# conn = sqlite3.connect("backend/db/cinemabot.db")
# cursor = conn.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = tuple(column_values.values())
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.execute(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Dict]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def is_user_registered(user_id: int) -> bool:
    cursor.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    rows = cursor.fetchall()
    return len(rows) > 0


def was_film_searched(film_id: int) -> bool:
    cursor.execute(f"SELECT film_id FROM films WHERE film_id = {film_id}")
    rows = cursor.fetchall()
    return len(rows) > 0


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    conn.commit()


def get_cursor():
    return cursor


def get_conn():
    return conn


# def check_db_exists():
#     cursor.execute("SELECT name FROM sqlite_master "
#                    "WHERE type='table' AND name='films'")
#     table_exists = cursor.fetchall()
#     if not table_exists:
#         _init_db()
