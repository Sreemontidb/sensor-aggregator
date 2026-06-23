import socket
import json
import threading
import time
import sys
import os

# Add project root to path so we can import database.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.database import init_db, insert_reading

HOST = "localhost"
PORT = 9999

# ── Tracks last heartbeat time per sensor ──────────────
# { "1": 1719123456.7, "2": 1719123459.2 }
last_seen = {}

# ── Anomaly detection ──────────────────────────────────
NORMAL_RANGES = {
    "temperature": (60, 90),
    "pressure"   : (30, 80)
}

def is_anomaly(data):
    for metric, (low, high) in NORMAL_RANGES.items():
        if not (low <= data[metric] <= high):
            return True
    return False

# ── Handle one sensor connection ───────────────────────
def handle_sensor(conn, addr):
    print(f"[Broker] Sensor connected from {addr}")
    buffer = ""

    try:
        while True:
            chunk = conn.recv(1024).decode()
            if not chunk:
                break  # sensor disconnected

            buffer += chunk

            # Messages are separated by \n
            # buffer may contain multiple messages at once
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue

                data = json.loads(line)
                anomaly = is_anomaly(data)

                # Update heartbeat
                last_seen[data["sensor_id"]] = time.time()

                # Save to DB
                insert_reading(data, anomaly)

                status = "⚠ ANOMALY" if anomaly else "OK"
                print(f"[Broker] Sensor-{data['sensor_id']} | "
                      f"Temp: {data['temperature']} | "
                      f"Pressure: {data['pressure']} | {status}")

    except Exception as e:
        print(f"[Broker] Error with {addr}: {e}")
    finally:
        conn.close()
        print(f"[Broker] Sensor {addr} disconnected")

# ── Heartbeat monitor (runs in background) ─────────────
def monitor_heartbeats():
    while True:
        time.sleep(5)
        now = time.time()
        for sensor_id, last in list(last_seen.items()):
            if now - last > 10:   # no data for 10 seconds → offline
                print(f"[Broker] ⚠ WARNING: Sensor-{sensor_id} appears OFFLINE")

# ── Main server loop ───────────────────────────────────
def run():
    init_db()
    print(f"[Broker] Starting on {HOST}:{PORT}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"[Broker] Listening for sensors...")

    # Start heartbeat monitor in background
    t = threading.Thread(target=monitor_heartbeats, daemon=True)
    t.start()

    while True:
        conn, addr = server.accept()
        # Each sensor gets its own thread
        t = threading.Thread(target=handle_sensor, args=(conn, addr))
        t.daemon = True
        t.start()

if __name__ == "__main__":
    run()