import sqlite3
import datetime

# Database Connection
def connect_db():
    return sqlite3.connect('chw_app.db')


def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    
    # Create patients table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100),
            age INT,
            gender VARCHAR(10),
            contact VARCHAR(50),
            bp VARCHAR(20),
            risk_score INT,
            next_appointment DATE
        )'''
    )

    # Create patient_records table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS patient_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INT REFERENCES patients(id),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            bp VARCHAR(10),
            risk_score INT,
            next_appointment DATE
        )'''
    )
    
    conn.commit()
    conn.close()

# Create Patient Record
def create_patient(name, age, gender, contact, bp, risk_score, next_appointment):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO patients (name, age, gender, contact, bp, risk_score, next_appointment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name, age, gender, contact, bp, risk_score, next_appointment),
    )
    conn.commit()
    conn.close()

# Read All Patients
def read_patients():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients")
    rows = cur.fetchall()
    columns = [column[0] for column in cur.description]  # Get column names
    conn.close()

    # Convert to a list of dictionaries
    return [dict(zip(columns, row)) for row in rows]

# Get a Specific Patient
def get_patient(patient_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        columns = [column[0] for column in cur.description]
        patient_data = dict(zip(columns, row))
        print("Fetched Patient Data:", patient_data)  # Debugging line
        return patient_data
    return None

# Update Patient Record and Track Changes
def update_patient(patient_id, bp=None, risk_score=None, next_appointment=None):
    conn = connect_db()
    cur = conn.cursor()
    
    # Update the main patient record
    query = "UPDATE patients SET "
    updates = []
    if bp:
        updates.append(f"bp = '{bp}'")
    if risk_score:
        updates.append(f"risk_score = {risk_score}")
    if next_appointment:
        updates.append(f"next_appointment = '{next_appointment}'")
    query += ", ".join(updates) + f" WHERE id = {patient_id}"
    cur.execute(query)
    
    # Insert into patient_records to track the update
    cur.execute(
        """
        INSERT INTO patient_records (patient_id, bp, risk_score, next_appointment)
        VALUES (?, ?, ?, ?)
        """,
        (patient_id, bp, risk_score, next_appointment)
    )
    
    conn.commit()
    conn.close()

# Function to Get Patient Overtime Data
def get_patient_overtime_data(patient_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patient_records WHERE patient_id = ? ORDER BY date DESC", (patient_id,))
    records = cur.fetchall()
    
    # Get column names
    columns = [column[0] for column in cur.description]
    
    conn.close()
    
    # Return records as a list of dictionaries
    return [dict(zip(columns, record)) for record in records]

# Delete Patient
def delete_patient(patient_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()
