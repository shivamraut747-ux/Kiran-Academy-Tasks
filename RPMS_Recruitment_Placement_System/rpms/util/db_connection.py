import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",  # Change as per your MySQL setup
    "database": "recruitment_portal"
}

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as exc:
        raise RuntimeError(f"Database connection failed: {exc}") from exc


# ---------------------------------------------------------------
# Helper functions (added in Phase 2)
# Every helper takes an optional "con" (connection).
#   - con not given -> helper opens its own connection, commits, closes it.
#   - con given     -> helper uses it and does NOT commit. The caller
#                      (a "transaction") decides when to commit / rollback.
# ---------------------------------------------------------------
from contextlib import contextmanager


def fetch_all(sql, params=(), con=None):
    """Run a SELECT and return all rows as a list of dictionaries."""
    own = con is None
    if own:
        con = get_connection()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        if own:
            con.close()


def fetch_one(sql, params=(), con=None):
    """Run a SELECT and return the first row (dictionary) or None."""
    rows = fetch_all(sql, params, con)
    return rows[0] if rows else None


def execute(sql, params=(), con=None):
    """Run INSERT / UPDATE / DELETE. Returns the new auto-increment id (for INSERT)."""
    own = con is None
    if own:
        con = get_connection()
    try:
        cur = con.cursor()
        cur.execute(sql, params)
        if own:
            con.commit()
        return cur.lastrowid
    finally:
        if own:
            con.close()


@contextmanager
def transaction():
    """
    Use for multi-table operations:

        with transaction() as con:
            dao_one.save(x, con)
            dao_two.save(y, con)

    Everything is committed together. If any line raises an error,
    everything is rolled back (nothing is saved).
    """
    con = get_connection()
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
