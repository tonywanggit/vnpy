from enum import Enum

from peewee import Database, MySQLDatabase, PostgresqlDatabase, SqliteDatabase
from vnpy.trader.utility import get_file_path

import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Driver(Enum):
    SQLITE = "sqlite"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


def init(driver: Driver, settings: dict):
    init_funcs = {
        Driver.SQLITE: init_sqlite,
        Driver.MYSQL: init_mysql,
        Driver.POSTGRESQL: init_postgresql,
    }
    assert driver in init_funcs

    db = init_funcs[driver](settings)
    return db


def init_sqlite(settings: dict):
    database = settings["database"]
    path = str(get_file_path(database))
    db = SqliteDatabase(path)
    return db


def init_mysql(settings: dict):
    keys = {"database", "user", "password", "host", "port"}
    settings = {k: v for k, v in settings.items() if k in keys}
    db = MySQLDatabase(**settings)
    return db


def init_postgresql(settings: dict):
    keys = {"database", "user", "password", "host", "port"}
    settings = {k: v for k, v in settings.items() if k in keys}
    db = PostgresqlDatabase(**settings)
    return db


def fetch_columns(driver: Driver, db: Database, table_name: str):
    if driver is Driver.SQLITE:
        c = db.execute_sql(f"PRAGMA table_info({table_name});")
        res = c.fetchall()
        return [i[1] for i in res]
    else:
        c = db.execute_sql(
            f"SELECT column_name "
            f"FROM INFORMATION_SCHEMA.COLUMNS "
            f"WHERE table_name = '{table_name}';"
        )
        res = c.fetchall()
        return [i[0] for i in res]


def upgrade(driver: Driver, db: Database):
    columns = fetch_columns(driver, db, "dbbardata")
    if 'open_interest' not in columns:
        db.execute_sql("ALTER TABLE dbbardata "
                       " ADD COLUMN open_interest FLOAT DEFAULT 0;")

    columns = fetch_columns(driver, db, "dbtickdata")
    if 'open_interest' not in columns:
        db.execute_sql("ALTER TABLE dbtickdata "
                       " ADD COLUMN open_interest FLOAT DEFAULT 0;")

    print("upgrade succeed!")


def down_grade(driver: Driver, db: Database):
    assert driver is not Driver.SQLITE  # sqlite doesn't support drop column

    columns = fetch_columns(driver, db, "dbbardata")
    if 'open_interest' in columns:
        db.execute_sql("ALTER TABLE dbbardata "
                       " DROP COLUMN open_interest;")

    columns = fetch_columns(driver, db, "dbtickdata")
    if 'open_interest' in columns:
        db.execute_sql("ALTER TABLE dbtickdata "
                       " DROP COLUMN open_interest;")

    print("down grade succeed!")


def main():
    from vnpy.trader.setting import get_settings

    settings = get_settings("database.")
    driver = Driver(settings["driver"])
    if driver is not Driver.MONGODB:
        db = init(driver, settings=settings)
        upgrade(driver, db)
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
