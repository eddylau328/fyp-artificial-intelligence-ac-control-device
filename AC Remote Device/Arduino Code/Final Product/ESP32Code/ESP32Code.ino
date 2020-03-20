#include <WiFi.h>
#include <FirebaseESP32.h>

#define WIFI_SSID "Lau Family"
#define WIFI_PASSWORD "27050880"
#define FIREBASE_HOST "fypacmonitor.firebaseio.com"
#define FIREBASE_AUTH "jaT833r4mymesl03s37FD9jeV9JnWZzcM1xrnX8d"


String serial_num = "fyp0001";
String firebase_sensor_address = String("/Devices/"+serial_num+"/sensors");
String firebase_receive_action = String("/Devices/"+serial_num+"/receive_action/command");
String firebase_receive_check_action = String("/Devices/"+serial_num+"/receive_action/is_sent");


//Define Firebase Data object
FirebaseData firebaseData;

// variable to hold the environment data
float temperature, humidity, light_intensity, pressure;

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

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  wifi_connect();
  firebase_connect();
  esp32_timer_initialize();
}

void loop() {
  // put your main code here, to run repeatedly:
  if (interruptCounter > 0){
    portENTER_CRITICAL(&timerMux);
    interruptCounter--;
    portEXIT_CRITICAL(&timerMux);
 
    totalInterruptCounter++;
    
    if (totalInterruptCounter % SEND_PEROID == 0){
      Serial.println("Done");
      totalInterruptCounter = 0;
    }
  }
}
