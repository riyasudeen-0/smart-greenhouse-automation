#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11

const int SOIL_PIN = A0;
const int PUMP_RELAY = 7;   // K1
const int FAN_RELAY  = 8;   // K2

// Soil calibration
const int DRY_RAW = 1023;
const int WET_RAW = 320;

// Automatic thresholds
const float PUMP_ON_LEVEL  = 35.0;
const float PUMP_OFF_LEVEL = 60.0;

const float FAN_ON_TEMP  = 32.0;
const float FAN_OFF_TEMP = 29.0;

DHT dht(DHTPIN, DHTTYPE);

bool pumpOn = false;
bool fanOn = false;
bool autoMode = true;

float getSoilPercent(int raw) {
  float percent =
    (float)(DRY_RAW - raw) * 100.0 /
    (DRY_RAW - WET_RAW);

  if (percent < 0) percent = 0;
  if (percent > 100) percent = 100;

  return percent;
}

void setPump(bool state) {
  pumpOn = state;
  digitalWrite(PUMP_RELAY, pumpOn ? LOW : HIGH);
}

void setFan(bool state) {
  fanOn = state;
  digitalWrite(FAN_RELAY, fanOn ? LOW : HIGH);
}

void processCommand(String command) {
  command.trim();
  command.toUpperCase();

  if (command == "AUTO") {
    autoMode = true;
    Serial.println("MODE,AUTO");
  }
  else if (command == "MANUAL") {
    autoMode = false;
    Serial.println("MODE,MANUAL");
  }
  else if (command == "PUMP_ON") {
    autoMode = false;
    setPump(true);
    Serial.println("COMMAND,PUMP_ON");
  }
  else if (command == "PUMP_OFF") {
    autoMode = false;
    setPump(false);
    Serial.println("COMMAND,PUMP_OFF");
  }
  else if (command == "FAN_ON") {
    autoMode = false;
    setFan(true);
    Serial.println("COMMAND,FAN_ON");
  }
  else if (command == "FAN_OFF") {
    autoMode = false;
    setFan(false);
    Serial.println("COMMAND,FAN_OFF");
  }
}

void readCommands() {
  while (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(PUMP_RELAY, OUTPUT);
  pinMode(FAN_RELAY, OUTPUT);

  // Start safely OFF
  setPump(false);
  setFan(false);

  dht.begin();

  Serial.println("SMART_GREENHOUSE_READY");
  Serial.println("MODE,AUTO");
}

void loop() {

  // Check for commands from Python/Flask
  readCommands();

  // Read sensors
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  int soilRaw = analogRead(SOIL_PIN);
  float soilPercent = getSoilPercent(soilRaw);

  // Automatic control
  if (autoMode) {

    // Pump hysteresis
    if (soilPercent <= PUMP_ON_LEVEL) {
      setPump(true);
    }
    else if (soilPercent >= PUMP_OFF_LEVEL) {
      setPump(false);
    }

    // Fan hysteresis
    if (!isnan(temperature)) {

      if (temperature >= FAN_ON_TEMP) {
        setFan(true);
      }
      else if (temperature <= FAN_OFF_TEMP) {
        setFan(false);
      }
    }
  }

  // CSV sensor data for Python
  Serial.print("DATA,");

  if (isnan(temperature))
    Serial.print("nan");
  else
    Serial.print(temperature, 1);

  Serial.print(",");

  if (isnan(humidity))
    Serial.print("nan");
  else
    Serial.print(humidity, 1);

  Serial.print(",");
  Serial.print(soilRaw);

  Serial.print(",");
  Serial.print(soilPercent, 1);

  Serial.print(",");
  Serial.print(pumpOn ? "ON" : "OFF");

  Serial.print(",");
  Serial.print(fanOn ? "ON" : "OFF");

  Serial.print(",");
  Serial.println(autoMode ? "AUTO" : "MANUAL");

  delay(2000);
}