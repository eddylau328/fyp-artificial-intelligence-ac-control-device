#include <ESP8266WiFi.h>
#include <ESP8266

const char* ssid="";
const char* password="";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println();
  Serial.print("Wifi connecting to ");
  Serial.println( ssid );

  WiFi.begin(ssid,password);

  Serial.println();
  Serial.print("Connecting");

  while( WiFi.status() != WL_CONNECTED ){
    Serial.print(".");
    delay(500);
  }

  Serial.println();

  Serial.println("Wifi Connected Success!");
  Serial.print("NodeMCU IP Address : ");
  Serial.println(WiFi.localIP());
  
  
}

void loop() {
  // put your main code here, to run repeatedly:

}
