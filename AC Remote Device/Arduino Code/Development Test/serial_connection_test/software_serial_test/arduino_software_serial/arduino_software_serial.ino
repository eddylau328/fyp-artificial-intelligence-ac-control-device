//Arduino code
#include <SoftwareSerial.h>

void setup() {
  Serial3.begin(9600);
}
 
void loop() {
 Serial3.println("Hello");
 delay(1000);
}
