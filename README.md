#  Smart Greenhouse Automation System

An IoT-based Smart Greenhouse Automation System built using Arduino Nano, Python, and Flask. The system monitors environmental conditions, automates irrigation and ventilation, and provides real-time monitoring through a web dashboard.

##  Project Overview

The Smart Greenhouse System is designed to monitor soil moisture, temperature, and humidity to help maintain suitable growing conditions.

It combines hardware sensors, an Arduino Nano microcontroller, relay-controlled devices, and a Python Flask web application.

##  Features

- Real-time temperature and humidity monitoring
- Soil moisture monitoring
- Automatic irrigation based on soil moisture levels
- Automatic fan control based on temperature
- Manual and automatic operating modes
- Weather information and forecast integration
- Live web dashboard
- Serial communication between Arduino and Python
- Data visualization and system status monitoring

##  Hardware Components

| Component | Purpose |
|---|---|
| Arduino Nano | Main microcontroller |
| DHT11 | Temperature and humidity monitoring |
| Soil Moisture Sensor | Measures soil moisture |
| 2-Channel Relay Module | Controls pump and fan |
| 12V DC Water Pump | Irrigation |
| 12V DC Fan | Temperature control |
| 12V DC Adapter | Powers the actuators |

##  Technologies Used

- Arduino IDE / C++
- Python
- Flask
- HTML, CSS and JavaScript
- PySerial
- Open-Meteo Weather API

##  System Architecture

The system consists of three main sections:

1. **Input:** DHT11 and soil moisture sensors collect environmental data.
2. **Processing:** Arduino Nano processes sensor readings and controls the relay module.
3. **Monitoring:** A Python Flask application communicates with Arduino through serial communication and displays information on a web dashboard.

Weather information is retrieved using the Open-Meteo API.

##  Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/smart-greenhouse-automation.git
cd smart-greenhouse-automation
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Upload Arduino code

Open the Arduino sketch inside the `arduino_code` folder using Arduino IDE and upload it to your Arduino Nano.

### 6. Run the Flask application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

**Note:** Make sure the correct Arduino serial port and baud rate are configured in `app.py`.

##  Working Principle

- The sensors continuously collect temperature, humidity, and soil moisture readings.
- Arduino processes the readings and controls the pump and fan through relays.
- The Flask application receives sensor data through USB serial communication.
- Weather information is retrieved from Open-Meteo.
- The web dashboard displays live readings and system status.
- Users can switch between automatic and manual control.


##  Project Information

**Project:** Smart Greenhouse Automation System

**Category:** Internet of Things (IoT)

**Platform:** Arduino Nano

**Backend:** Python Flask

---

Built as an academic project to explore IoT, embedded systems, automation, and web-based monitoring.