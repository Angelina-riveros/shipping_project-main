import sqlite3

DB_NAME = "ground_shipping.db" # This file will store your database

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows dict-like access to rows
    return conn