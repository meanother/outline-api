import sqlite3
import pathlib
from typing import Optional

home_dir = pathlib.Path.home()
home_dir.joinpath("db").mkdir(parents=True, exist_ok=True)


database_path = home_dir.joinpath("db") / "outline.db"

# if not database_path.exists():
#     raise FileNotFoundError(f"file {database_path} not found")


conn = sqlite3.connect(database_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def _init_db():
    """Инициализирует БД"""
    init_path = pathlib.Path(__file__).resolve().parent.parent / "init.sql"
    if init_path.exists():
        with open(init_path, "r", encoding='utf-8') as file:
            init_src = file.read()
        cursor.executescript(init_src)
        conn.commit()
    else:
        raise FileNotFoundError("Init db file not found!")


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute(
        "SELECT count(*) FROM sqlite_master WHERE name = 'outline_users'"
    )
    table_exists = cursor.fetchone()[0]
    if table_exists == 1:
        return
    _init_db()


def insert(table: str, column_values: dict):
    """insert Dict to sqlite3 tables"""
    columns = ", ".join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(f"INSERT INTO {table} " f"({columns}) " f"VALUES ({placeholders})", values)
    conn.commit()


def select_user(username: str) -> Optional[dict]:
    cursor.execute("select key_id, name, access_url from outline_users where name = ?", (username, ))
    user_data = cursor.fetchone()
    if user_data:
        return dict(zip(user_data.keys(), user_data))
    return {}


def update_user_limit(username: str, limit: str) -> Optional[dict]:
    cursor.execute("update outline_users set data_limit = ? where name = ?", (username, limit))
    return select_user(username)


def delete_user(username: str) -> None:
    cursor.execute("delete from outline_users where name = ?", (username, ))


check_db_exists()
