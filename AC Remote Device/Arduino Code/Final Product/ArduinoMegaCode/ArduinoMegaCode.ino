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

// used to check whether need to send data to nodemcu or not
bool isSendData = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial3.begin(115200);
  bmp.begin();
  htu.begin();
  bh.begin();

  lcd.begin(16, 2);
  delay(50);
}

float temperature,pressure,humidity,light_intensity;

void readEnvironment() {
  temperature = htu.readTemperature()+temperature_offset;
  delay(100);
  pressure = ceil(bmp.readPressure()/100)/10;
  delay(100);
  humidity = htu.readHumidity();
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
  StaticJsonBuffer<1000> doc;
  JsonObject& data =doc.createObject();
  data["temp"] = temperature;
  data["hum"] = humidity;
  data["light"] = light_intensity;
  data["press"] = pressure;
  data.prettyPrintTo(Serial3);
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
  
  if (isSendData == true){
    send_data_2_nodemcu();
    // after finish sending the data, isSendData=false
    isSendData = false;
  }
  
  while(Serial3.available() > 0){
    if (Serial3.read() == 'a' && isSendData == false){
      isSendData = true;
    }
  }

  lcd_print_environment_data();
  delay(50);
}
