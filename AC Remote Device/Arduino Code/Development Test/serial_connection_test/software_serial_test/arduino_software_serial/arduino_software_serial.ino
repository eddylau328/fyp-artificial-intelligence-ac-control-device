//Arduino code

void setup() {
  Serial3.begin(9600);
}
 
void loop() {
 Serial3.println("Hello");
 if(Serial3.available() > 0){
  Serial.println("Receive");
 }
 delay(1000);
}
