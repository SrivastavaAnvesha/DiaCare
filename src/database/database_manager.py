import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create patients table
        c.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create diabetes_records table
        c.execute('''
            CREATE TABLE IF NOT EXISTS diabetes_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                pregnancies INTEGER,
                glucose REAL,
                blood_pressure REAL,
                skin_thickness REAL,
                insulin REAL,
                bmi REAL,
                diabetes_pedigree REAL,
                prediction INTEGER,
                probability REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # Create ulcer_records table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ulcer_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                image_path TEXT,
                prediction TEXT,
                probability REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_patient(self, name, age, gender):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO patients (name, age, gender)
            VALUES (?, ?, ?)
        ''', (name, age, gender))
        
        patient_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return patient_id
    
    def add_diabetes_record(self, patient_id, data, prediction, probability):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO diabetes_records 
            (patient_id, pregnancies, glucose, blood_pressure, skin_thickness,
             insulin, bmi, diabetes_pedigree, prediction, probability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, data['pregnancies'], data['glucose'],
              data['blood_pressure'], data['skin_thickness'],
              data['insulin'], data['bmi'], data['diabetes_pedigree'],
              prediction, probability))
        
        record_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def add_ulcer_record(self, patient_id, image_path, prediction, probability):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO ulcer_records 
            (patient_id, image_path, prediction, probability)
            VALUES (?, ?, ?, ?)
        ''', (patient_id, image_path, prediction, probability))
        
        record_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_patient_records(self, patient_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Get patient info
        c.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
        patient = dict(c.fetchone())
        
        # Get diabetes records
        c.execute('SELECT * FROM diabetes_records WHERE patient_id = ?', (patient_id,))
        diabetes_records = [dict(row) for row in c.fetchall()]
        
        # Get ulcer records
        c.execute('SELECT * FROM ulcer_records WHERE patient_id = ?', (patient_id,))
        ulcer_records = [dict(row) for row in c.fetchall()]
        
        conn.close()
        
        return {
            'patient': patient,
            'diabetes_records': diabetes_records,
            'ulcer_records': ulcer_records
        }
