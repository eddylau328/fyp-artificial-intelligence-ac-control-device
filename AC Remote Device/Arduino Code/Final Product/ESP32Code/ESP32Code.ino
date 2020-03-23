#include <WiFi.h>
#include <FirebaseESP32.h>
#include <ArduinoJson.h>
#include <HardwareSerial.h>

#define RXD1 9
#define TXD1 10
#define RXD2 16
#define TXD2 17

#define WIFI_SSID "Lau Family"
#define WIFI_PASSWORD "27050880"
#define FIREBASE_HOST "fypacmonitor.firebaseio.com"
#define FIREBASE_AUTH "jaT833r4mymesl03s37FD9jeV9JnWZzcM1xrnX8d"


String serial_num = "fyp0001";
String firebase_sensor_address = String("/Devices/"+serial_num+"/sensors");
String firebase_receive_action = String("/Devices/"+serial_num+"/receive_action/command");
String firebase_receive_check_action = String("/Devices/"+serial_num+"/receive_action/is_new_action");
String firebase_start_send = String("/Devices/"+serial_num+"/receive_action/is_send");
String firebase_ac_status_power = String("/Devices/"+serial_num+"/ac_status/power_state");
String firebase_ac_status_temp = String("/Devices/"+serial_num+"/ac_status/set_temp");
String firebase_ac_status_fanspeed = String("/Devices/"+serial_num+"/ac_status/set_fanspeed");
String firebase_parse_fail = String("Devices/"+serial_num+"/error/parse_fail");

//Define Firebase Data object
FirebaseData firebaseData;

//
bool request_data = false;
// state of whether it is connected to wifi or not
bool isConnectedWifi = false;
// state that whether it is sending data to firebase or not
bool isSendData2Firebase = false;

int parse_fail_count = 0;

// variable to hold the environment data
float temperature, humidity, light_intensity, pressure;

int ir_fanspeed=1, ir_temp=24, ir_power=0;

void wifi_connect(){
  //connect to WiFi
  Serial.printf("Connecting to %s ", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println(" CONNECTED");
}

void firebase_connect(){
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
}

void send_data_2_firebase(){
  FirebaseJson json_data;
  json_data.add("temp", temperature);
  json_data.add("hum", humidity);
  json_data.add("light", light_intensity);
  json_data.add("press", pressure);
  
  if (Firebase.pushJSON(firebaseData, firebase_sensor_address, json_data))
  {
    Serial.println("PUSHED");
  }
  else
  {
    Serial.println("FAILED");
    Serial.println("REASON: " + firebaseData.errorReason());
    Serial.println("------------------------------------");
    Serial.println();
  }
}

// Interrupt Timer
// ---------------------------------------------------------------------------
volatile int interruptCounter;
int totalInterruptCounter;
const int SEND_PEROID = 10;

hw_timer_t * esp32_timer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
 
void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);
  interruptCounter++;
  portEXIT_CRITICAL_ISR(&timerMux);
 
}

void esp32_timer_initialize(){
  esp32_timer = timerBegin(0, 80, true);
  timerAttachInterrupt(esp32_timer, &onTimer, true);
  timerAlarmWrite(esp32_timer, 1000000, true);
  timerAlarmEnable(esp32_timer);
}

// ---------------------------------------------------------------------------

void receive_json_data(){
  StaticJsonBuffer<256> doc;
  // deserialize the object
  JsonObject& data = doc.parseObject(Serial2);
  if (!data.success()) {
     Serial.println("parseObject() failed");
     parse_fail_count++;
  }else{
    if (data.containsKey("temp")){
      // save the received data
      temperature = data["temp"];
      humidity = data["hum"];
      light_intensity = data["light"];
      pressure = data["press"];
    }else{
      ir_power = data["ir_power"];
      ir_temp = data["ir_temp"];
      ir_fanspeed = data["ir_fanspeed"];
    }
  }
}

// Send Command To MEGA 2560
// ---------------------------------------------------------------------------
void send_wifi_status_2_mega(bool status){
  if (status == true)
    Serial.println("wifi on");
  else
    Serial.println("wifi off");
}

bool check_new_command_from_firebase(){
  bool isNewCommand;
  Firebase.getBool(firebaseData, firebase_receive_check_action, isNewCommand);
  return isNewCommand;
}

void set_is_new_command_from_firebase(bool flag){
  Firebase.setBool(firebaseData, firebase_receive_check_action, flag);
}

String get_command_from_firebase(){
  String command = "";
  Firebase.getString(firebaseData, firebase_receive_action, command);
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


void check_is_send_2_firebase(){
  Firebase.getBool(firebaseData, firebase_start_send, isSendData2Firebase);
}

// ---------------------------------------------------------------------------


void update_firebase_error_count(){
  int tempCount;
  Firebase.getInt(firebaseData, firebase_parse_fail, tempCount);
  if (tempCount != parse_fail_count)
    Firebase.setInt(firebaseData, firebase_parse_fail, parse_fail_count);
}


void update_firebase_ac_status(){
  int fb_fanspeed, fb_temp;
  bool fb_power;
  Firebase.getBool(firebaseData, firebase_ac_status_power, fb_power);
  Firebase.getInt(firebaseData, firebase_ac_status_temp, fb_temp);
  Firebase.getInt(firebaseData, firebase_ac_status_fanspeed, fb_fanspeed);

  if (fb_power != (bool)ir_power){
    Firebase.setBool(firebaseData, firebase_ac_status_power, (bool)ir_power);
  }

  if (fb_temp != ir_temp){
    Firebase.setInt(firebaseData, firebase_ac_status_temp, ir_temp);
  }

  if (fb_fanspeed != ir_fanspeed){
    Firebase.setInt(firebaseData, firebase_ac_status_fanspeed, ir_fanspeed);
  }
  
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
  delay(1000);
  wifi_connect();
  firebase_connect();
  esp32_timer_initialize();
}

void loop() {
  // put your main code here, to run repeatedly:
  // Interrupt Timer part
  if (interruptCounter > 0){
    portENTER_CRITICAL(&timerMux);
    interruptCounter--;
    portEXIT_CRITICAL(&timerMux);
    
    if (isSendData2Firebase)
      totalInterruptCounter++;
    else
      totalInterruptCounter = 0;

    if ((totalInterruptCounter % SEND_PEROID) == (SEND_PEROID - 3)){
      request_data = true;
    }
    
    if (totalInterruptCounter % SEND_PEROID == 0){
      if (isSendData2Firebase)
        send_data_2_firebase();
      totalInterruptCounter = 0;
    }
  }

  if(Serial2.available() > 0)
    receive_json_data();

  check_is_send_2_firebase();
  
  if (check_new_command_from_firebase() || request_data){
    if (request_data){
      send_command_2_mega("data poll");
      request_data = false;
    }else{
      String command = get_command_from_firebase();
      if (send_command_2_mega(command)){
        set_is_new_command_from_firebase(false);
      }
    }
  }

  update_firebase_ac_status();
  update_firebase_error_count();
  
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

}
