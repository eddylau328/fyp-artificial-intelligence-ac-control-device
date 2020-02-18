#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>
#include <ArduinoJson.h>
#include <LiquidCrystal.h>
#include <Timer.h>
#include "DHT.h"

#define DHTPIN 8     // Digital pin connected to the DHT sensor

#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
DHT dht(DHTPIN, DHTTYPE);
// LCD 1602 setup
LiquidCrystal lcd(12,11,37,35,33,31);

// Setup a communication way between arduino mega and nodemcu

Adafruit_BMP085 bmp;

BH1750 bh;

// used to check whether need to send data to nodemcu or not
bool isSendData = false;

Timer nodemcu_sendtimer;
long int nodemcu_sendtimerInterval = 2000;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(74880);
  Serial2.begin(74880);
  Serial3.begin(74880);
  
  bmp.begin();
  bh.begin();
  dht.begin();
  
  lcd.begin(16, 2);
  delay(50);
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

void loop() {
  // put your main code here, to run repeatedly:
  readEnvironment();
  lcd.clear();
  if (nodemcu_sendtimer.checkfinish()){
    send_data_2_nodemcu();
    nodemcu_sendtimer.resettimer();
    nodemcu_sendtimer.starttimer();
  }

  if (Serial3.available() > 0){
    
  }

  lcd_print_environment_data();
  
}
