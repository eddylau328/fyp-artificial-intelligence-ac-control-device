#include <SoftwareSerial.h>
SoftwareSerial s(D6,D5);
int data;
void setup() {
s.begin(9600);
Serial.begin(9600);
}
 
void loop() {
  if (s.available()>0)
  {
    Serial.write(s.read());
  }
}
