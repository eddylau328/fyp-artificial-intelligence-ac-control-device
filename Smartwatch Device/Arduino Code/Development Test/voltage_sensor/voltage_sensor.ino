void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

int sensor_value;

int offset = 200;

void loop() {
  // put your main code here, to run repeatedly:
  sensor_value = analogRead(39) + 200;
  float volt = (sensor_value*3.3/4095)*(30000+7500)/7500;
  Serial.println(volt);
  delay(1000);
}
