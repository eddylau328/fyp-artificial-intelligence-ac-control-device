#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

// Set these to run example.
#define FIREBASE_HOST "datalog-418c9.firebaseio.com"
#define FIREBASE_AUTH "txdD1XvFjmWd2BTuyEU8ztwa4D5OZESobTSUCARv"
#define WIFI_SSID "Eddy Wifi"
#define WIFI_PASSWORD "12345678xd"  // hidden for credentials problem

SoftwareSerial s(D7,D8);

void setup() {
  Serial.begin(9600);
  s.begin(9600);
  
  // connect to wifi.
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("connecting");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("connected: ");
  Serial.println(WiFi.localIP());
  
  Firebase.begin(FIREBASE_HOST);
  
}

void loop() 
{
  if (s.available() > 0){
    StaticJsonBuffer<1000> doc;
    // deserialize the object
    JsonObject& data = doc.parseObject(s);
    if (!data.success()) {
       Serial.println("parseObject() failed");
       return;
    }
    Serial.println();
    data.prettyPrintTo(Serial);
    delay(50);
    Serial.println();
    Serial.println("Received");
    Serial.println();
    String name = Firebase.push("/sensor", data);
    if (Firebase.failed()) {
      Serial.print("Firebase Pushing /sensor failed:");
      Serial.println(Firebase.error()); 
      return;
    }else{
      Serial.print("Firebase Pushed /sensor ");
      Serial.println(name);
    }
  }else{
    Serial.print(".");
    delay(50);
  }
}
