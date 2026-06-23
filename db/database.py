import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sensor_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id   TEXT,
            temperature REAL,
            pressure    REAL,
            timestamp   REAL,
            is_anomaly  INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Database ready.")

def insert_reading(data, anomaly):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO sensor_data 
        (sensor_id, temperature, pressure, timestamp, is_anomaly)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data["sensor_id"],
        data["temperature"],
        data["pressure"],
        data["timestamp"],
        1 if anomaly else 0
    ))
    conn.commit()
    conn.close()

def get_recent_readings(limit=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT sensor_id, temperature, pressure, timestamp, is_anomaly
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows