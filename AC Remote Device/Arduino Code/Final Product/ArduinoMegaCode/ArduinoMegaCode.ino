#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>
#include <ArduinoJson.h>
#include <LiquidCrystal.h>

// LCD 1602 setup
LiquidCrystal lcd(12,11,37,35,33,31);

// Setup a communication way between arduino mega and nodemcu

Adafruit_BMP085 bmp;
Adafruit_HTU21DF htu;
float temperature_offset = -0.92;
BH1750 bh;

int second = 0;
// every 60s, 1 min per data
int dataLogPeriod = 60;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial3.begin(9600);
  bmp.begin();
  htu.begin();
  bh.begin();

  lcd.begin(16, 2);
  
  delay(50);
}

float temperature,pressure,humidity,light_intensity;

void readEnvironment() {
  temperature = htu.readTemperature()+temperature_offset;
  pressure = ceil(bmp.readPressure()/100)/10;
  humidity = htu.readHumidity();
  light_intensity = bh.readLightLevel();
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

void loop() {
  // put your main code here, to run repeatedly:
  readEnvironment();

  if (second == 0){
    StaticJsonBuffer<1000> doc;
    JsonObject& root =doc.createObject();
    root["temp"] = temperature;
    root["hum"] = humidity;
    root["light"] = light_intensity;
    root["press"] = pressure;
    root.prettyPrintTo(Serial3);
  }
  
  LCDprint(temperature, 0, 0, false);
  LCDprint((char)223,6,0,false);
  LCDprint("C",7,0,false);
  
  LCDprint(humidity,9,0,false);
  LCDprint("%",15,0,false);
  
  LCDprint(pressure,0,1,false);
  LCDprint("kPa",5,1,false);
  
  LCDprint((int)light_intensity,9,1,false);
  LCDprint("lx",14,1,false);
  delay(1000);
  second += 1;
  if (second >= dataLogPeriod){
    second = 0;
  }
}
