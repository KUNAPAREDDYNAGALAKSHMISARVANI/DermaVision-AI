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
    # Appointments Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            doctor_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            patient_phone TEXT NOT NULL,
            patient_email TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'Confirmed',
            created_at TEXT NOT NULL,
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


def save_appointment(user_id, doctor_id, patient_name, patient_phone, patient_email, appointment_date, appointment_time, notes=""):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO appointments (
            user_id,
            doctor_id,
            patient_name,
            patient_phone,
            patient_email,
            appointment_date,
            appointment_time,
            notes,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?)
    """, (
        user_id,
        doctor_id,
        patient_name,
        patient_phone,
        patient_email,
        appointment_date,
        appointment_time,
        notes,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    app_id = cursor.lastrowid
    connection.close()
    return app_id


def get_user_appointments(user_id=None):
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if user_id:
        cursor.execute("SELECT * FROM appointments WHERE user_id = ? ORDER BY appointment_date ASC, appointment_time ASC", (user_id,))
    else:
        cursor.execute("SELECT * FROM appointments WHERE (user_id IS NULL OR user_id = '') ORDER BY appointment_date ASC, appointment_time ASC")

    rows = cursor.fetchall()
    connection.close()
    return rows


def get_upcoming_appointment(user_id=None):
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")

    if user_id:
        cursor.execute("""
            SELECT * FROM appointments 
            WHERE user_id = ? AND appointment_date >= ? AND status != 'Cancelled'
            ORDER BY appointment_date ASC, appointment_time ASC LIMIT 1
        """, (user_id, today_str))
    else:
        cursor.execute("""
            SELECT * FROM appointments 
            WHERE (user_id IS NULL OR user_id = '') AND appointment_date >= ? AND status != 'Cancelled'
            ORDER BY appointment_date ASC, appointment_time ASC LIMIT 1
        """, (today_str,))

    row = cursor.fetchone()
    connection.close()
    return row


def cancel_appointment(appointment_id, user_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    if user_id:
        cursor.execute("UPDATE appointments SET status = 'Cancelled' WHERE id = ? AND user_id = ?", (appointment_id, user_id))
    else:
        cursor.execute("UPDATE appointments SET status = 'Cancelled' WHERE id = ? AND (user_id IS NULL OR user_id = '')", (appointment_id,))

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()