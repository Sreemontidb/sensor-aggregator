from flask import Flask, render_template, jsonify
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.database import get_recent_readings

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    rows = get_recent_readings(100)
    readings = []
    for r in rows:
        readings.append({
            "sensor_id" : r[0],
            "temperature": r[1],
            "pressure"   : r[2],
            "timestamp"  : r[3],
            "is_anomaly" : r[4]
        })
    return jsonify(readings)

if __name__ == "__main__":
    app.run(debug=True, port=5000)