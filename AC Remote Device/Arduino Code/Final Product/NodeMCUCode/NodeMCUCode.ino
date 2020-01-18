#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

// Set these to run example.
#define FIREBASE_HOST "fypacmonitor.firebaseio.com"
#define FIREBASE_AUTH "jaT833r4mymesl03s37FD9jeV9JnWZzcM1xrnX8d"
#define WIFI_SSID "Eddy Wifi"
#define WIFI_PASSWORD "12345678xd"  // hidden for credentials problem

SoftwareSerial s(D7,D8); //D2, D1
String serial_num = "fyp0001";
String firebase_sensor_address = String("/Devices/"+serial_num+"/sensors");
String firebase_receive_action = String("/Devices/"+serial_num+"/receive_action");



void setup() {
  Serial.begin(115200);
  s.begin(115200);
  
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

int count = 0;
bool isWorking = false;

void loop() 
{
  
  if (isWorking == false){
    s.write("a");
    isWorking = true;
  }
  
  if (Serial.available() > 0){
    s.write("a");
  }
  
  if (s.available() > 0){
    count = 0;
    
    StaticJsonBuffer<1000> doc;
    // deserialize the object
    JsonObject& data = doc.parseObject(s);
    if (!data.success()) {
       Serial.println("parseObject() failed");
       return;
    }
    Serial.println();
    data.prettyPrintTo(Serial);
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

    Serial.println("Need Request");
    isWorking = true;
  }else{
    count ++;
  }

  if (count > 10){
    isWorking = false;
    count = 0;
  }
  delay(500);
}
