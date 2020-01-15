#include <Wire.h>
#include <BH1750.h>
#include <ArduinoJson.h>
#include <LiquidCrystal.h>
#include <SoftwareSerial.h>

// LCD 1602 setup
LiquidCrystal lcd(12,11,37,35,33,31);

// Setup a communication way between arduino mega and nodemcu

BH1750 bh;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial3.begin(9600);
  bh.begin();

  lcd.begin(16, 2);

  LCDprint("Connecting", 0, 0, false);
  int i = 0;
  while (Serial3.available() == 0){
    if (i > 5){
      LCDprint("Connecting", 0, 0, true);
      i = -1;
    }else{
      LCDprint(".", i+10, 0, false);
    }
    i++;
    delay(1000);
  }

  lcd.clear();
  
  delay(50);
}

float temperature,pressure,humidity,light_intensity;

void readEnvironment() {
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

  if (Serial3.available() > 0){
    
    StaticJsonBuffer<1000> doc;
    // deserialize the object
    JsonObject& data = doc.parseObject(Serial3);
    if (!data.success()) {
       Serial.println("parseObject() failed");
       return;
    }

    temperature = data["temp"];
    humidity = data["hum"];
    humidity = ceil(humidity/100)*10;
    pressure = data["press"];
    
  }else{
    StaticJsonBuffer<1000> doc;
    JsonObject& root =doc.createObject();
    root["light"] = light_intensity;
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
}
