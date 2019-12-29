#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>
#include <ArduinoJson.h>

Adafruit_BMP085 bmp;
Adafruit_HTU21DF htu;
BH1750 bh;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial3.begin(9600);
  bmp.begin();
  htu.begin();
  bh.begin();
  delay(50);
}

float temperature,pressure,humidity,light_intensity;

void readEnvironment() {
  temperature = htu.readTemperature();
  pressure = bmp.readPressure();
  humidity = htu.readHumidity();
  light_intensity = bh.readLightLevel();
}

void loop() {
  // put your main code here, to run repeatedly:
  readEnvironment();
  StaticJsonBuffer<1000> doc;
  JsonObject& root =doc.createObject();
  root["temp"] = temperature;
  root["hum"] = humidity;
  root["light"] = light_intensity;
  root["press"] = pressure;
  root.prettyPrintTo(s);
  root.prettyPrintTo(Serial3);
  delay(1000);
}
