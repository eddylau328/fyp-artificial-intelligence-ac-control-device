//Arduino code
#include <SoftwareSerial.h>
SoftwareSerial s(5,6);
 
void setup() {
s.begin(9600);
}
 
void loop() {
 s.println("Hello");
}
