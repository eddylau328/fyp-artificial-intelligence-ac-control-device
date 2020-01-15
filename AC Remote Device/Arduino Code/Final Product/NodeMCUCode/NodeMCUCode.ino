#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>

// Set these to run example.
#define FIREBASE_HOST "datalog-418c9.firebaseio.com"
#define FIREBASE_AUTH "txdD1XvFjmWd2BTuyEU8ztwa4D5OZESobTSUCARv"
#define WIFI_SSID "Eddy Wifi"
#define WIFI_PASSWORD "12345678xd"  // hidden for credentials problem

SoftwareSerial s(D7,D8);
Adafruit_BMP085 bmp;
Adafruit_HTU21DF htu;

int second = 0;
// every 60s, 1 min per data
int dataLogPeriod = 60;

void setup() {
  Serial.begin(9600);
  s.begin(9600);

  bmp.begin();
  htu.begin();

  
  // connect to wifi.
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("connecting");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("connected: ");
  s.print("Connected");
  Serial.println(WiFi.localIP());
  
  Firebase.begin(FIREBASE_HOST);
  
}

float temperature,pressure,humidity,light_intensity;

void readEnvironment() {
  temperature = htu.readTemperature();
  pressure = bmp.readPressure();
  humidity = htu.readHumidity();
}

void loop() 
{
  readEnvironment();
  //Serial.println(temperature);
  //Serial.println(humidity);
  //Serial.println(pressure);
  //Serial.println(light_intensity);
  
  if (s.available() > 0){
    StaticJsonBuffer<1000> doc;
    // deserialize the object
    JsonObject& root = doc.parseObject(s);
    if (!root.success()) {
       Serial.println("parseObject() failed");
       return;
    }

    light_intensity = root["light"];
    Serial.println(light_intensity);
    /*JsonObject& data =doc.createObject();
    data["temp"] = temperature;
    data["hum"] = humidity;
    data["light"] = light_intensity;
    data["press"] = pressure;
    data.prettyPrintTo(s);
    data.prettyPrintTo(Serial);
    */
  }

  if (second == dataLogPeriod) {
    StaticJsonBuffer<1000> doc;
    JsonObject& data =doc.createObject();
    data["temp"] = temperature;
    data["hum"] = humidity;
    data["light"] = light_intensity;
    data["press"] = pressure;
    
    String name = Firebase.push("/sensor", data);
    if (Firebase.failed()) {
      Serial.print("Firebase Pushing /sensor failed:");
      Serial.println(Firebase.error()); 
      return;
    }else{
      Serial.print("Firebase Pushed /sensor ");
      Serial.println(name);
    }
  }
  
  second += 1;
  if (second >= dataLogPeriod){
    second = 0;
  }

  delay(500);
}
