#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
SoftwareSerial s(5,6);

Adafruit_BMP085 bmp;
Adafruit_HTU21DF htu;
BH1750 bh;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  s.begin(9600);
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
  delay(5000);
}
