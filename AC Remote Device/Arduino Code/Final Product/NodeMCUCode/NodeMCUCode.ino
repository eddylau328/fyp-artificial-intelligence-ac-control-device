#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <Timer.h>

// Set these to run example.
#define FIREBASE_HOST "fypacmonitor.firebaseio.com"
#define FIREBASE_AUTH "jaT833r4mymesl03s37FD9jeV9JnWZzcM1xrnX8d"
#define WIFI_SSID "Eddy Wifi"
#define WIFI_PASSWORD "12345678xd"  // hidden for credentials problem

//SoftwareSerial s(D7,D8); //D2, D1
String serial_num = "fyp0001";
String firebase_sensor_address = String("/Devices/"+serial_num+"/sensors");
String firebase_receive_action = String("/Devices/"+serial_num+"/receive_action");


// 60 seconds timer
Timer firebase_sendtimer;
long int firebase_sendtimerInterval = 10000;

// check whether the step_num in the machine learning 
int step_num;
int action;

float temperature, humidity, light_intensity, pressure;

SoftwareSerial s(D7,D8);

void setup() {
  Serial.begin(74880);
  s.begin(74880);
  
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

  instantiateTimers();

  step_num = 0;
}

void instantiateTimers(){
  firebase_sendtimer.settimer(firebase_sendtimerInterval);
  firebase_sendtimer.starttimer();
}

void send_data_2_firebase(){
    StaticJsonBuffer<1000> doc;
    JsonObject& data =doc.createObject();
    data["temp"] = temperature;
    data["hum"] = humidity;
    data["light"] = light_intensity;
    data["press"] = pressure;

    //firebase send sensor data action
    String name = Firebase.push(firebase_sensor_address, data);
    if (Firebase.failed()) {
      Serial.print("Firebase Pushing /sensor failed:");
      Serial.println(Firebase.error()); 
      return;
    }else{
      Serial.print("Firebase Pushed /sensor ");
      Serial.println(name);
    }  
}

void loop() 
{
  
  if (s.available() > 0){
    StaticJsonBuffer<256> doc;
    // deserialize the object
    JsonObject& data = doc.parseObject(s);
    if (!data.success()) {
       Serial.println("parseObject() failed");
    }else{
      // save the received data
      temperature = data["temp"];
      humidity = data["hum"];
      light_intensity = data["light"];
      pressure = data["press"];
    }
  }
    
  if (firebase_sendtimer.checkfinish()){
    send_data_2_firebase();
    firebase_sendtimer.resettimer();
    firebase_sendtimer.starttimer();
  }
  
}

  /*
  // when receiving the data send from the arduino
  if (s.available() > 0){
    StaticJsonBuffer<1000> doc;
    // deserialize the object
    JsonObject& data = doc.parseObject(s);
    if (!data.success()) {
       Serial.println("parseObject() failed");
       return;
    }

    // save the received data
    temperature = data["temp"];
    humidity = data["hum"];
    light_intensity = data["light"];
    pressure = data["press"];
    
    data.prettyPrintTo(Serial);
  }
  */
