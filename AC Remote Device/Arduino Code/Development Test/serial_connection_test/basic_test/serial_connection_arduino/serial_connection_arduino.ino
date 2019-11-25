void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  delay(2000);
}
 
void loop() {
  Serial.println("Hello");
  Serial1.println("Hello");
  delay(5000);
}
