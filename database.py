import sqlite3
import os
from datetime import datetime

DATABASE_FOLDER = "database"
DATABASE_NAME = "dermavision.db"

DATABASE_PATH = os.path.join(DATABASE_FOLDER, DATABASE_NAME)


def create_database():
    

    if not os.path.exists(DATABASE_FOLDER):
        os.makedirs(DATABASE_FOLDER)

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        image TEXT NOT NULL,

        disease TEXT NOT NULL,

        confidence REAL NOT NULL,

        scan_date TEXT NOT NULL,

        notes TEXT

    )
    """)

    connection.commit()

    connection.close()

    print("Database created successfully!")
def save_scan(image, disease, confidence):

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute("""

        INSERT INTO scans
        (

            image,

            disease,

            confidence,

            scan_date,

            notes

        )

        VALUES (?, ?, ?, ?, ?)

    """,

    (

        image,

        disease,

        confidence,

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        ""

    ))

    connection.commit()

    connection.close()