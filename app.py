from flask import Flask, jsonify, render_template, request
import serial
import threading
import time
import requests

app = Flask(__name__)

# -----------------------------
# Arduino
# -----------------------------
PORT = "COM3"
BAUD = 9600

latest_data = {
    "temperature": None,
    "humidity": None,
    "soil_raw": None,
    "soil_percent": None,
    "pump": "OFF",
    "fan": "OFF",
    "mode": "AUTO",
}

ser = None
serial_lock = threading.Lock()

# -----------------------------
# Weather
# -----------------------------
LATITUDE = 10.7273
LONGITUDE = 76.2899

weather_data = {
    "rain_probability": None,
    "forecast_temperature": None,
    "rain_next_3h": 0.0,
    "updated": False,
}


def connect_serial():
    global ser

    while True:
        try:
            ser = serial.Serial(PORT, BAUD, timeout=2)
            time.sleep(2)
            print(f"Connected to Arduino on {PORT}")
            return
        except serial.SerialException as e:
            print(f"Waiting for Arduino: {e}")
            time.sleep(3)


def send_command(command):
    global ser

    with serial_lock:
        if ser is None or not ser.is_open:
            return False

        try:
            ser.write((command + "\n").encode("utf-8"))
            ser.flush()
            print(f"Sent command: {command}")
            return True

        except serial.SerialException as e:
            print(f"Command error: {e}")
            return False


def read_arduino():
    global latest_data

    connect_serial()

    while True:
        try:
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            print("Arduino:", line)

            if not line.startswith("DATA,"):
                continue

            parts = line.split(",")

            if len(parts) != 8:
                continue

            latest_data = {
                "temperature":
                    None if parts[1] == "nan"
                    else float(parts[1]),

                "humidity":
                    None if parts[2] == "nan"
                    else float(parts[2]),

                "soil_raw": int(parts[3]),
                "soil_percent": float(parts[4]),
                "pump": parts[5],
                "fan": parts[6],
                "mode": parts[7],
            }

        except (ValueError, serial.SerialException) as e:
            print("Serial read error:", e)
            time.sleep(1)


def fetch_weather():
    global weather_data

    while True:
        try:
            url = "https://api.open-meteo.com/v1/forecast"

            params = {
                "latitude": LATITUDE,
                "longitude": LONGITUDE,
                "hourly": (
                    "temperature_2m,"
                    "precipitation_probability,"
                    "rain,"
                    "precipitation,"
                    "weather_code"
                ),
                "forecast_days": 1,
                "timezone": "auto",
            }

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            hourly = data["hourly"]

            probabilities = hourly["precipitation_probability"]
            temperatures = hourly["temperature_2m"]
            rain = hourly["rain"]

            # First forecast hour
            weather_data["rain_probability"] = probabilities[0]
            weather_data["forecast_temperature"] = temperatures[0]

            # Total expected rain over next 3 hours
            weather_data["rain_next_3h"] = sum(rain[:3])

            weather_data["updated"] = True

            print(
                "Weather updated:",
                weather_data
            )

        except (requests.RequestException, KeyError, IndexError) as e:
            print("Weather error:", e)

        # Update weather every 10 minutes
        time.sleep(600)


def get_irrigation_decision():
    soil = latest_data["soil_percent"]

    rain_probability = weather_data["rain_probability"]
    rain_next_3h = weather_data["rain_next_3h"]

    if soil is None:
        return {
            "status": "WAITING",
            "reason": "Waiting for soil sensor data."
        }

    if soil >= 60:
        return {
            "status": "NO IRRIGATION",
            "reason": "Soil moisture is already sufficient."
        }

    if soil <= 35:

        if rain_probability is not None and (
            rain_probability >= 60 or rain_next_3h >= 1.0
        ):
            return {
                "status": "DELAY IRRIGATION",
                "reason": "Soil is dry, but rainfall is expected soon."
            }

        return {
            "status": "IRRIGATE NOW",
            "reason": "Soil is dry and significant rain is not expected."
        }

    return {
        "status": "MONITORING",
        "reason": "Soil moisture is in the intermediate range."
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    result = dict(latest_data)

    result["weather"] = weather_data
    result["irrigation_decision"] = get_irrigation_decision()

    return jsonify(result)


@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json(silent=True) or {}

    command = str(
        data.get("command", "")
    ).strip().upper()

    allowed_commands = {
        "AUTO",
        "MANUAL",
        "PUMP_ON",
        "PUMP_OFF",
        "FAN_ON",
        "FAN_OFF",
    }

    if command not in allowed_commands:
        return jsonify({
            "success": False,
            "error": "Invalid command"
        }), 400

    success = send_command(command)

    if success:
        return jsonify({
            "success": True,
            "command": command
        })

    return jsonify({
        "success": False,
        "error": "Arduino serial connection unavailable"
    }), 503


if __name__ == "__main__":

    arduino_thread = threading.Thread(
        target=read_arduino,
        daemon=True
    )

    weather_thread = threading.Thread(
        target=fetch_weather,
        daemon=True
    )

    arduino_thread.start()
    weather_thread.start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )