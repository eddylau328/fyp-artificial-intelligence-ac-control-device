#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <Timer.h>

// Set these to run example.
#define FIREBASE_HOST "fypacmonitor.firebaseio.com"
#define FIREBASE_AUTH "jaT833r4mymesl03s37FD9jeV9JnWZzcM1xrnX8d"
#define WIFI_SSID "Lau Family"
#define WIFI_PASSWORD "27050880"  // hidden for credentials problem

//SoftwareSerial s(D7,D8); //D2, D1
String serial_num = "fyp0001";
const String firebase_sensor_address = String("/Devices/"+serial_num+"/sensors");
const String firebase_receive_action = String("/Devices/"+serial_num+"/receive_action/command");
const String firebase_receive_check_action = String("/Devices/"+serial_num+"/receive_action/is_sent");

// 60 seconds timer
Timer firebase_sendtimer;
long int firebase_sendtimerInterval = 10000;

// check whether the step_num in the machine learning 
int step_num;
int action;

// variable to hold the environment data
float temperature, humidity, light_intensity, pressure;

// state of whether it is connected to wifi or not
bool isConnectedWifi = false;
// state that whether it is sending data to firebase or not
bool isSendData2Firebase = false;

SoftwareSerial s(D7,D8);

void instantiateTimers(){
  firebase_sendtimer.settimer(firebase_sendtimerInterval);
  firebase_sendtimer.starttimer();
}

void send_data_2_firebase(){
    StaticJsonBuffer<100> doc;
    JsonObject& data =doc.createObject();
    data["temp"] = temperature;
    data["hum"] = humidity;
    data["light"] = light_intensity;
    data["press"] = pressure;

    //firebase send sensor data action
    String name = Firebase.push(firebase_sensor_address, data);
    /*
    if (Firebase.failed()) {
      Serial.print("Firebase Pushing /sensor failed:");
      Serial.println(Firebase.error()); 
      return;
    }else{
      Serial.print("Firebase Pushed /sensor ");
      Serial.println(name);
    }
    */
}

bool check_new_command_from_firebase(){
  bool isNewCommand = Firebase.getBool(firebase_receive_check_action);
  return isNewCommand;
}

void set_is_new_command_from_firebase(bool flag){
  Firebase.setBool(firebase_receive_check_action, flag);
}

String get_command_from_firebase(){
  String command = Firebase.getString(firebase_receive_action);
  return command;
}

bool send_command_2_mega(String command){
  if (!Serial.available()){
    Serial.println(command);
    return true;
  }else{
    return false;
  }
}

void send_wifi_status_2_mega(bool status){
  if (status == true)
    Serial.println("wifi on");
  else
    Serial.println("wifi off");
}


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

  isConnectedWifi = true;
  send_wifi_status_2_mega(true);
  
  Firebase.begin(FIREBASE_HOST);

  instantiateTimers();

  step_num = 0;
}


void loop() 
{
  
  if (s.available() > 0){
    StaticJsonBuffer<100> doc;
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
    if (isConnectedWifi && isSendData2Firebase){
      Serial.println("pass");
      send_data_2_firebase();
    }
    
    firebase_sendtimer.resettimer();
    firebase_sendtimer.starttimer();
  }

  if (check_new_command_from_firebase()){
    String command = get_command_from_firebase();
    if (send_command_2_mega(command)){
      set_is_new_command_from_firebase(false);
    }
  }
  /*
  if (WiFi.status() != WL_CONNECTED){
    if (isConnectedWifi){
      send_wifi_status_2_mega(false);
      isConnectedWifi = false;
    }
  }else if (WiFi.status() == WL_CONNECTED){
    if (!isConnectedWifi){
      send_wifi_status_2_mega(true);
      isConnectedWifi = true;
    }
  }
  */
}
