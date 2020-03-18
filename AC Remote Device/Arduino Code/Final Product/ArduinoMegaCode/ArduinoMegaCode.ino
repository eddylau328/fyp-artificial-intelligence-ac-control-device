#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>
#include <ArduinoJson.h>
#include <LiquidCrystal.h>
#include <Timer.h>
#include "DHT.h"
// For IR control------------
#include <IRremote.h>
#include "IRmonitor.h"
// Define the IR send Object
// For mega2560 is pin 9 (currently cannot modify)
IRsend irsend;
IRmonitor ir_monitor;
// --------------------------

#define DHTPIN 8     // Digital pin connected to the DHT sensor

#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
DHT dht(DHTPIN, DHTTYPE);
// LCD 1602 setup
LiquidCrystal lcd(12,11,37,35,33,31);

// Setup a communication way between arduino mega and nodemcu

Adafruit_BMP085 bmp;

BH1750 bh;

Timer nodemcu_sendtimer;
long int nodemcu_sendtimerInterval = 2000;

class SendAction{
  public:
    String name;
    int id;
    ControlAction(){}
    void create(String name, int id){
      this->name = name;
      this->id = id;
    }
};

#define TOTAL_SEND_FUNCTION 3
#define SEND_DATA 0
#define SEND_WIFI_STATUS 1
#define SEND_IR 2

SendAction send_actions[TOTAL_SEND_FUNCTION];

void control_action_initialize(){
  send_actions[0].create("data", SEND_DATA);
  send_actions[1].create("wifi", SEND_WIFI_STATUS);
  send_actions[2].create("ir", SEND_IR);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial2.begin(115200);
  Serial3.begin(115200);
  /*
  bmp.begin();
  bh.begin();
  dht.begin();
  
  lcd.begin(16, 2);
  delay(50);
  */
  control_action_initialize();
  nodemcu_sendtimer.settimer(nodemcu_sendtimerInterval);
  nodemcu_sendtimer.starttimer();
}

float temperature,pressure,humidity,light_intensity;

void readEnvironment() {
  temperature = dht.readTemperature();
  delay(100);
  pressure = ceil(bmp.readPressure()/100)/10;
  delay(100);
  humidity = dht.readHumidity();
  delay(100);
  light_intensity = bh.readLightLevel();
  delay(100);
}

// 0 <= x <= 15 (15 can only print one digit)
// 0 or 1 for y (row 1 and row 2)
void LCDprint(String str, int x, int y, bool clearScreen){
  if (clearScreen)
    lcd.clear();
  lcd.setCursor(x,y);
  lcd.print(str);
}

void LCDprint(float num, int x, int y, bool clearScreen){
  if (clearScreen)
    lcd.clear();
  lcd.setCursor(x,y);
  lcd.print(num);
}

void LCDprint(int num, int x, int y, bool clearScreen){
  if (clearScreen)
    lcd.clear();
  lcd.setCursor(x,y);
  lcd.print(num);
}

void LCDprint(char ch, int x, int y, bool clearScreen){
  if (clearScreen)
    lcd.clear();
  lcd.setCursor(x,y);
  lcd.print(ch);
}

// send json object to nodemcu
// json object contain the environment data
void send_data_2_nodemcu(){
  StaticJsonBuffer<256> doc;
  JsonObject& data =doc.createObject();
  data["temp"] = temperature;
  data["hum"] = humidity;
  data["light"] = light_intensity;
  data["press"] = pressure;
  data.prettyPrintTo(Serial2);
  data.prettyPrintTo(Serial);
}

// print the environment data on the LCD1602
void lcd_print_environment_data(){
  LCDprint(temperature, 0, 0, false);
  LCDprint((char)223,6,0,false);
  LCDprint("C",7,0,false);
  
  LCDprint(humidity,9,0,false);
  LCDprint("%",15,0,false);
  
  LCDprint(pressure,0,1,false);
  LCDprint("kPa",5,1,false);
  
  LCDprint((int)light_intensity,9,1,false);
  LCDprint("lx",14,1,false);
}

void sendIRByCommand(String command){
  if (ir_monitor.checkCommand(command)){
    ir_monitor.sendCommand(irsend, command);
  }
}

String serial3_getMessage(){
  String command;
  while(Serial3.available()) {
    command= Serial3.readString();// read the incoming data as string
    // remove input command possible enter character
    for (int i = command.length(); i >= 0; i++)
      if (command[i] == "\n"){
        command[i] = "\0";
        break;
      }
  }
  return command;
}

int check_send_action_id(String command){
  bool flag = false;
  for (int i = 0; i < TOTAL_SEND_FUNCTION; i++){
    flag = true;
    for (int j = 0; j < send_actions[i].name.length(); j++){
      if (send_actions[i].name[j] != command[j]){
        flag = false;
        break;
      }
    }
    if (flag == true){
      return i;
    }
  }
  return -1;
}

String remove_command_name(String command, int command_id){
  String command_value = "";
  String temp = "";
  for (int i = send_actions[command_id].name.length()+1; i < command.length(); i++){
    temp += command[i];
  }
  for (int i = 0; i < temp.length(); i++){
    if (temp[i] != '\n'){
      command_value += temp[i];
    }
  }
  return command_value;
}

void loop() {
  /*
  // put your main code here, to run repeatedly:
  readEnvironment();
  lcd.clear();
  if (nodemcu_sendtimer.checkfinish()){
    send_data_2_nodemcu();
    nodemcu_sendtimer.resettimer();
    nodemcu_sendtimer.starttimer();
  }
  */
  if (Serial3.available() > 0){
    String command = serial3_getMessage();
    int command_id = check_send_action_id(command);
    String command_value = remove_command_name(command, command_id);
    switch(command_id)
    {
      case(SEND_DATA):
        Serial.print(command_value);
        break;
      case(SEND_WIFI_STATUS):
        Serial.print(command_value);
        break;
      case(SEND_IR):
        Serial.print(command_value);
        break;
    }
  }

  lcd_print_environment_data();
  
}
