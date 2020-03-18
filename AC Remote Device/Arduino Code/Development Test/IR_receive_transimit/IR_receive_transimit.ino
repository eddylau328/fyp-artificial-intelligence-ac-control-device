#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>

#include <IRremote.h>
#include "IRmonitor.h"

// Define the switch pin
const int switchPin = 7;
const int modePin = 3;
// Button state
int buttonstate = 0;
int modeButtonState = 0;
int currentMode = 0;

// Define the IR send Object
// For mega2560 is pin 9 (currently cannot modify)
IRsend irsend;

// Define the IR sensor pin
const int RECV_PIN = 4;
// Define the IR receiver and result object
IRrecv irrecv(RECV_PIN);
decode_results results;

Adafruit_BMP085 bmp;
Adafruit_HTU21DF htu;
BH1750 bh;

IRmonitor ir_monitor;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  delay(500);
  bmp.begin();
  htu.begin();
  bh.begin();

  // Enable the ir receiver
  irrecv.enableIRIn();

  // Set the switchPin as input
  pinMode(switchPin, INPUT);
  pinMode(modePin, INPUT);

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

void decodeIR() {
  if (irrecv.decode(&results)){
    switch (results.decode_type){
      case NEC: 
        Serial.println("NEC"); 
        break;
      case SONY: 
        Serial.println("SONY"); 
        break;
      case RC5: 
        Serial.println("RC5"); 
        break;
      case RC6: 
        Serial.println("RC6"); 
        break;
      case DISH: 
        Serial.println("DISH"); 
        break;
      case SHARP: 
        Serial.println("SHARP"); 
        break;
      case JVC: 
        Serial.println("JVC"); 
        break;
      case SANYO: 
        Serial.println("SANYO"); 
        break;
      case MITSUBISHI: 
        Serial.println("MITSUBISHI"); 
        break;
      case SAMSUNG: 
        Serial.println("SAMSUNG"); 
        break;
      case LG: 
        Serial.println("LG"); 
        break;
      case WHYNTER: 
        Serial.println("WHYNTER"); 
        break;
      case AIWA_RC_T501: 
        Serial.println("AIWA_RC_T501"); 
        break;
      case PANASONIC: 
        Serial.println("PANASONIC"); 
        break;
      case DENON: 
        Serial.println("DENON"); 
        break;
    default:
      case UNKNOWN: 
        Serial.println("UNKNOWN"); 
        break;
    }
    
    // print code
    for (int i=1; i < results.rawlen; i++){
      Serial.print(results.rawbuf[i]*USECPERTICK, DEC);
      Serial.print(" ");
    }
    Serial.println();
    Serial.print("Length = ");
    Serial.print(results.rawlen-1);
    Serial.println();
    
    irrecv.resume();
  }  
}

void sendIRByButton(unsigned int raw[], int rawlen) {
  // Set buttonstate depending upon switch position
  buttonstate = digitalRead(switchPin);
  // If the button is pressed, send ir signals
  if (buttonstate == HIGH){
    irsend.sendRaw(raw, rawlen, 38);
    Serial.println("send");
    // Enable the ir receiver
    irrecv.enableIRIn();
  }
}

void sendIR(unsigned int raw[], int rawlen) {
  irsend.sendRaw(raw, rawlen, 38);
  Serial.println("send");
  // Enable the ir receiver
  irrecv.enableIRIn();
}

String command;

void sendIRByCommand(){
  while(Serial.available()) {
    command= Serial.readString();// read the incoming data as string
    // remove input command possible enter character
    for (int i = command.length() - 1; i >= 0; i++)
      if (command[i] == "\n"){
        command[i] = "\0";
        break;
      }
    if (ir_monitor.checkCommand(command)){
      ir_monitor.sendCommand(irsend, command);
    }
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  // readEnvironment(1);
  //decodeIR();
  sendIRByCommand();
  //sendIRByButton(modeList[currentMode],signal_len);
  delay(500);
}
