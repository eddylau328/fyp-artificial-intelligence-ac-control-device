#include <SoftwareSerial.h>
SoftwareSerial s(D7,D8);

void setup() {
  Serial.begin(9600);
  s.begin(9600);
}

int i = 0;

void loop() {

  if (i >= 30){
    i = 0;
    s.println("nodemcu");
  }
  
  if (Serial.available()>0)
  {
    while(Serial.available() > 0){
      Serial.write(Serial.read());
    }
    i++;
  }
}
