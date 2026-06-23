import socket
import json
import random
import time
import sys

# ── Identity ──────────────────────────────────────────
# We pass sensor ID from command line so we can run
# multiple sensors without changing code
# e.g: python sensor.py 1
SENSOR_ID = sys.argv[1] if len(sys.argv) > 1 else "1"

BROKER_HOST = "localhost"
BROKER_PORT = 9999

# ── Simulated reading ranges ───────────────────────────
# Mostly normal, but 10% chance of anomaly spike
def get_reading():
    if random.random() < 0.10:   # 10% chance → anomaly
        temperature = random.uniform(110, 130)   # dangerously high
        pressure    = random.uniform(95, 110)
    else:
        temperature = random.uniform(60, 90)     # normal range
        pressure    = random.uniform(30, 80)

    return {
        "sensor_id"  : SENSOR_ID,
        "temperature": round(temperature, 2),
        "pressure"   : round(pressure, 2),
        "timestamp"  : time.time()
    }

# ── Connection + send loop ─────────────────────────────
def run():
    while True:   # keeps trying to reconnect if broker is down
        try:
            print(f"[Sensor-{SENSOR_ID}] Connecting to broker...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((BROKER_HOST, BROKER_PORT))
            print(f"[Sensor-{SENSOR_ID}] Connected.")

            while True:
                data = get_reading()
                message = json.dumps(data) + "\n"  # \n is our message separator
                sock.sendall(message.encode())
                print(f"[Sensor-{SENSOR_ID}] Sent: {data}")
                time.sleep(2)   # send every 2 seconds

        except (ConnectionRefusedError, BrokenPipeError) as e:
            print(f"[Sensor-{SENSOR_ID}] Connection lost: {e}. Retrying in 5s...")
            time.sleep(5)   # wait then reconnect → fault tolerance

if __name__ == "__main__":
    run()