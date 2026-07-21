import sqlite3
import os
from datetime import datetime

DATABASE_FOLDER = "database"
DATABASE_NAME = "dermavision.db"
DATABASE_PATH = os.path.join(DATABASE_FOLDER, DATABASE_NAME)


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def create_database():

    if not os.path.exists(DATABASE_FOLDER):
        os.makedirs(DATABASE_FOLDER)

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------
    # Users Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # -----------------------------
    # Scans Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image TEXT NOT NULL,
            disease TEXT NOT NULL,
            confidence REAL NOT NULL,
            scan_date TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # -----------------------------
    # Upgrade older databases
    # -----------------------------
    cursor.execute("PRAGMA table_info(scans)")
    columns = [column[1] for column in cursor.fetchall()]

    if "user_id" not in columns:
        cursor.execute("ALTER TABLE scans ADD COLUMN user_id INTEGER")

    connection.commit()
    connection.close()

    print("Database initialized successfully!")


def save_scan(user_id, image, disease, confidence):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO scans (
            user_id,
            image,
            disease,
            confidence,
            scan_date,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        image,
        disease,
        confidence,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ""
    ))

    connection.commit()
    connection.close()
    
if __name__ == "__main__":
    create_database()