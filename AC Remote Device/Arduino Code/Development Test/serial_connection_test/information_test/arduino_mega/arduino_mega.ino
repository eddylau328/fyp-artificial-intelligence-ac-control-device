#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>

Adafruit_BMP085 bmp;
Adafruit_HTU21DF htu;
BH1750 bh;

// Define the switch pin
const int switchPin = 7;
// Button state
int buttonstate = 0;
int isSend = 1;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial1.begin(9600);
  delay(500);
  bmp.begin();
  htu.begin();
  bh.begin();

  pinMode(switchPin, INPUT);
  
  delay(500);
}

float temperature,pressure,humidity,light_intensity;

void readEnvironment(int isDisplay) {
  temperature = htu.readTemperature();
  pressure = bmp.readPressure();
  humidity = htu.readHumidity();
  light_intensity = bh.readLightLevel();

  if (isDisplay == 1)
  {
    Serial.println("Record");
    Serial.print("Temperature = ");
    Serial.print(temperature);
    Serial.print(" *c");
    Serial.println();
    
    Serial.print("Pressure = ");
    Serial.print(pressure);
    Serial.print(" Pa");
    Serial.println();
      
    Serial.print("Humidity = ");
    Serial.print(humidity);
    Serial.print(" %");
    Serial.println();
      
    Serial.print("Light Intensity = ");
    Serial.print(light_intensity);
    Serial.print(" lux");
    Serial.println();
  }
}

void sendEnvironment(){
  if (isSend == 1){
    Serial1.print("Temperature = ");
    Serial1.print(temperature);
    Serial1.print(" *c");
    Serial1.println();
    
    Serial1.print("Pressure = ");
    Serial1.print(pressure);
    Serial1.print(" Pa");
    Serial1.println();
      
    Serial1.print("Humidity = ");
    Serial1.print(humidity);
    Serial1.print(" %");
    Serial1.println();
      
    Serial1.print("Light Intensity = ");
    Serial1.print(light_intensity);
    Serial1.print(" lux");
    Serial1.println();
    Serial1.println();
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  readEnvironment(1);
  sendEnvironment();
  // Set buttonstate depending upon switch position
  buttonstate = digitalRead(switchPin);
  // If the button is pressed, send ir signals
  if (buttonstate == HIGH){
    isSend = !isSend;
    if (isSend == 1){
      Serial.println("\nStart send records!!\n");
      Serial1.println("\nStart send records!!\n");
    } else {
      Serial.println("\nStop send records!!\n");
      Serial1.println("\nStop send records!!\n");
    }
  }
  
  delay(2000);
}
