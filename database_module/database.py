import sqlite3
from datetime import datetime
import os

DB_FILE = "diacare_db.sqlite3"

# Get connection
def get_connection():
    return sqlite3.connect(DB_FILE)

# Create tables if not exist
def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS diabetes_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            glucose REAL,
            blood_pressure REAL,
            bmi REAL,
            diabetes_pedigree REAL,
            prediction INTEGER,
            confidence REAL,
            timestamp TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS foot_ulcer_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            image_path TEXT,
            prediction INTEGER,
            confidence REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Insert diabetes record
def insert_diabetes_record(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO diabetes_records
        (name, age, glucose, blood_pressure, bmi, diabetes_pedigree, prediction, confidence, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'], data['age'], data['glucose'], data['blood_pressure'],
        data['bmi'], data['diabetes_pedigree'], data['prediction'],
        data['confidence'], datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# Insert foot ulcer record
def insert_foot_ulcer_record(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO foot_ulcer_records
        (name, age, image_path, prediction, confidence, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data['name'], data['age'], data['image_path'],
        data['prediction'], data['confidence'], datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# Fetch records
def fetch_records(table_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name} ORDER BY id DESC")
    records = cur.fetchall()
    conn.close()
    return records

# Initialize the database tables on import
create_tables()

# Export a helper class for easy import in app.py
class DatabaseModule:
    def fetch_records(self, table_name):
        return fetch_records(table_name)
    
    def insert_diabetes_record(self, data):
        return insert_diabetes_record(data)
        
    def insert_foot_ulcer_record(self, data):
        return insert_foot_ulcer_record(data)

database = DatabaseModule()