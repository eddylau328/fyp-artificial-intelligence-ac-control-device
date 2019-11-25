#include <ESP8266WiFi.h>
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>

#define TRIGGER_PIN D2

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(500);
  WiFiManager wifiManager;
  wifiManager.resetSettings();
  wifiManager.setBreakAfterConfig(true);
  
  Serial.println("Conecting.....");
  wifiManager.autoConnect("Test","fyp123");
  Serial.println("connected");
  pinMode(TRIGGER_PIN, INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if ( digitalRead(TRIGGER_PIN) == LOW ) {
    Serial.println("done");
  }
}
