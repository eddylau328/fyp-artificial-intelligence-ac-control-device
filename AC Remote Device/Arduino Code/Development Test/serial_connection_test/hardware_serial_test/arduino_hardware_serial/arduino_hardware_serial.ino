//Arduino code

void setup() {
  Serial.begin(9600);
  Serial2.begin(9600);
  Serial3.begin(9600);
}
 
void loop() {
 Serial3.println("mega2560");
 if(Serial2.available() > 0){
    while(Serial2.available() > 0){
      Serial.write(Serial2.read());
    }
 }
 delay(1000);
}
