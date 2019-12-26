#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

// Set these to run example.
#define FIREBASE_HOST "datalog-418c9.firebaseio.com"
#define FIREBASE_AUTH "txdD1XvFjmWd2BTuyEU8ztwa4D5OZESobTSUCARv"
#define WIFI_SSID "Lau Family"
#define WIFI_PASSWORD "27050880"  // hidden for credentials problem

SoftwareSerial s(D6,D5);

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
    String name = Firebase.push("/sensor/data", data);
    if (Firebase.failed()) {
      Serial.print("Firebase Pushing /sensor/data failed:");
      Serial.println(Firebase.error()); 
      return;
    }else{
      Serial.print("Firebase Pushed /sensor/data ");
      Serial.println(name);
    }
  }else{
    Serial.print(".");
    delay(50);
  }
  /*
  if (Serial.available() > 0){
    StaticJsonBuffer<1000> doc;
    // deserialize the object
    JsonObject& data = doc.parseObject(Serial);
    if (!data.success()) {
       Serial.println("parseObject() failed");
       return;
    }
    // extract the data
    float temperature = data["temp"];
    float humidity = data["hum"];
    float pressure = data["press"];
    float light_intensity = data["light"];
    String name = Firebase.push("/sensor/data", data);
    if (Firebase.failed()) {
      Serial.print("Firebase Pushing /sensor/data failed:");
      Serial.println(Firebase.error()); 
      return;
    }else{
      Serial.print("Firebase Pushed /sensor/data ");
      Serial.println(name);
    }
  }else{
    Serial.print(".");
    delay(50);
  }
  */
}
