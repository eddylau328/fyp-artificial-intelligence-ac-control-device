#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>

#include <IRremote.h>

// Define the switch pin
const int switchPin = 7;
const int modePin = 3;
// Button state
int buttonstate = 0;
int modeButtonState = 0;
int currentMode = 0;

// Define the IR send Object
IRsend irsend;
int fanstate = 0;
unsigned int speed1[101] = {3500,3350,950,750,900,800,950,750,950,750,950,2500,950,2450,1000,700,950,2500,950,750,950,750,900,800,950,750,950,2500,950,2450,950,800,950,2450,900,800,1000,2450,900,2500,950,750,950,2500,950,2450,1000,700,950,750,950,800,900,2500,950,2500,950,750,950,2450,950,2500,900,800,950,750,3500,3350,950,750,950,750,950,750,950,800,900,2500,950,2450,1000,750,950,2450,950,750,950,750,950,800,950,750,900,2500,950,2500,950,750,950,2450};
unsigned int speed2[101] = {3550,3300,950,2450,1000,700,1000,700,1050,2400,950,750,1000,700,950,2500,950,750,950,2450,1000,700,1000,750,950,2450,950,750,1000,700,1050,2400,950,750,1000,700,950,2500,950,750,1000,2400,1000,700,1000,750,950,750,950,750,950,750,1000,2450,1000,700,950,2450,950,750,1000,700,1000,750,950,750,3550,3300,950,2450,1000,700,1000,750,950,2450,1000,700,950,750,950,2500,950,750,1000,2400,1000,750,1000,700,950,2450,1000,700,1000,750,1000,2400,950,750};
unsigned int speed3[101] = {3550,3300,1000,2450,950,750,1000,700,950,2500,950,750,950,2450,1000,2450,950,750,950,2450,1000,750,900,800,950,2450,1000,700,950,2500,950,2450,1000,700,1000,750,950,2450,950,750,950,2500,900,800,950,750,1000,700,950,750,1000,700,950,2500,950,750,950,2450,1000,750,950,750,950,750,1000,700,3550,3300,1000,2450,950,750,950,750,950,2450,1000,750,950,2450,950,2450,1000,750,950,2450,950,750,1000,700,950,2500,950,750,950,2450,950,2500,950,750};
unsigned int switchFanSpeed[52] = {3350,3250,850,2450,900,2450,850,800,850,2450,850,2450,850,2450,850,2500,850,2450,850,2450,850,2450,850,2450,900,750,900,800,850,800,850,2450,850,800,850,800,900,750,900,750,850,800,850,800,900,800,850,800,850,2450,850};
unsigned int onoffFan[52] = {3400,3250,850,2450,900,2400,900,750,900,2400,900,2450,900,2400,900,750,950,700,900,750,900,750,950,700,900,2400,950,750,900,750,900,2400,900,750,900,750,900,750,950,2350,950,2400,900,2400,900,2400,900,2400,950,700,950};
int signal_len = 101;
unsigned int modeList[3][101];



#define TOTAL_SIGNALS 10
#define SIGNAL_LENGTH 100


class IRsignal{
  public:
    String command;
    int ir_size;
    unsigned int ir_wave[SIGNAL_LENGTH];
    // constructor
    IRsignal(){}
    // constructor
    IRsignal(String command, unsigned int ir_wave[], int ir_size){
      create(command, ir_wave, ir_size);
    }
    
    void create(String command, unsigned int ir_wave[], int ir_size){
      this->command = command;
      this->ir_size = ir_size;
      for (int i = 0; i < 100; i++)
        this->ir_wave[i] = ir_wave[i];
    }
};


// Define the IR sensor pin
const int RECV_PIN = 4;
// Define the IR receiver and result object
IRrecv irrecv(RECV_PIN);
decode_results results;

Adafruit_BMP085 bmp;
Adafruit_HTU21DF htu;
BH1750 bh;

IRsignal signals[TOTAL_SIGNALS];
/*
Commands
- "poweron"
- "poweroff"
- "+temp"
- "-temp"
- "fanspeed"
- "mode"
- "swingon"
- "swingoff"
- "economyon"
- "economyoff"
*/
void IRsignals_command_setup(){
  unsigned int tmpArray[TOTAL_SIGNALS][100] = {
      {4450,4250,600,1600,600,450,600,1550,600,1600,600,450,600,500,600,1550,600,500,600,500,600,1550,600,450,650,450,600,1550,600,1600,600,450,600,1550,600,500,600,1550,600,1600,600,1550,550,1600,600,500,600,1550,600,1550,600,1550,600,500,600,500,600,450,600,500,550,1600,600,500,600,500,600,1550,600,1550,600,1550,600,500,550,550,600,450,600,500,600,500,600,450,600,500,600,500,600,1550,550,1600,600,1550,600,1550,600,1600,500},
      {4500,4200,600,1600,600,450,700,1450,650,1550,600,450,650,450,600,1550,650,450,600,450,650,1550,600,450,600,500,650,1500,650,1500,650,450,600,1550,650,450,600,500,600,1550,600,1550,650,1500,650,1500,650,1500,650,1550,650,1500,650,1500,650,450,600,450,650,450,650,450,600,450,600,500,600,500,600,1550,650,400,650,450,650,450,600,450,600,500,650,450,600,1550,650,450,600,1550,650,1500,650,1500,600,1550,650,1500,650,1550,500},
      {4450,4250,650,1500,600,500,600,1550,650,1500,700,400,650,450,600,1550,600,500,650,400,650,1500,600,500,650,450,650,1500,600,1550,650,450,600,1550,600,1550,600,500,650,450,600,1550,600,1550,600,1550,650,1500,600,1550,650,450,650,1500,650,1500,650,450,600,500,600,450,700,400,600,500,600,1550,700,1450,650,450,600,450,650,450,650,450,600,450,700,400,650,450,650,400,650,1550,600,1550,600,1550,650,1500,650,1500,650,1550,500},
      {4450,4250,650,1500,650,450,650,1500,600,1550,600,500,600,500,600,1550,650,450,600,450,650,1550,600,450,600,500,600,1550,650,1500,650,450,600,1550,600,1550,650,450,650,450,600,1550,650,1500,600,1550,650,1500,650,1550,600,450,600,1600,600,1550,650,400,650,450,650,450,600,450,600,500,600,500,600,1550,600,500,600,450,650,450,600,500,600,450,650,450,600,1550,650,450,600,1550,600,1550,650,1550,600,1550,650,1500,600,1550,500},
      {4400,4300,600,1550,600,450,600,1600,600,1550,600,450,600,500,650,1500,650,450,600,500,650,1500,650,450,600,450,600,1550,650,1550,600,450,650,1550,600,450,650,450,650,450,600,1550,600,1550,600,1550,650,1500,650,1500,650,1550,600,1550,600,1550,600,500,650,400,700,400,650,450,600,450,650,450,650,1500,600,500,600,1550,650,450,600,1550,600,500,600,500,600,1550,600,500,650,1500,600,450,650,1550,600,450,650,1550,600,1550,500},
      {4500,4250,650,1500,650,450,650,1500,650,1500,650,450,650,450,650,1500,600,450,650,450,650,1500,650,450,650,450,650,1500,650,1500,600,500,600,1550,600,500,600,450,650,450,650,450,650,1500,600,1550,650,1500,650,1500,700,1500,600,1550,600,1550,600,1550,600,500,600,500,600,450,650,450,650,1500,650,1500,650,1550,600,450,650,450,600,500,650,400,650,450,650,450,650,400,650,450,600,1550,650,1500,650,1500,700,1500,650,1500,500},
      {4400,4300,600,1600,600,450,600,1550,600,1600,600,450,600,500,600,1550,600,500,600,450,650,1550,600,450,600,500,600,1550,600,1550,650,450,650,1500,600,1600,600,1550,600,1550,600,500,550,500,600,500,600,450,650,450,600,500,600,450,650,450,600,1550,600,1550,650,1550,600,1550,550,1600,650,450,600,450,650,450,600,500,550,500,650,450,600,1550,600,1550,650,1550,600,1550,600,1550,600,1550,600,1550,600,1550,650,450,600,500,500}
    }; 
  signals[0].create("poweron", tmpArray[0], SIGNAL_LENGTH);
  signals[1].create("poweroff", tmpArray[0], SIGNAL_LENGTH);
  signals[2].create("fanspeed", tmpArray[1], SIGNAL_LENGTH);
  signals[3].create("+temp", tmpArray[2], SIGNAL_LENGTH);
  signals[4].create("-temp", tmpArray[3], SIGNAL_LENGTH);
  signals[5].create("mode", tmpArray[4], SIGNAL_LENGTH); 
  signals[6].create("swingon", tmpArray[5], SIGNAL_LENGTH);
  signals[7].create("swingoff", tmpArray[5], SIGNAL_LENGTH);
  signals[8].create("economyon", tmpArray[6], SIGNAL_LENGTH);
  signals[9].create("economyoff", tmpArray[6], SIGNAL_LENGTH);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  delay(500);
  bmp.begin();
  htu.begin();
  bh.begin();
  IRsignals_command_setup();
  // Enable the ir receiver
  irrecv.enableIRIn();
  
  // Set the switchPin as input
  pinMode(switchPin, INPUT);
  pinMode(modePin, INPUT);

  delay(500);
  for (int i=0; i<signal_len; i++){
    modeList[0][i] = speed1[i];
    modeList[1][i] = speed2[i];
    modeList[2][i] = speed3[i];
  }
  currentMode = 0;
  
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
    Serial.print(results.rawlen);
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

void automatic_control(){
  if (temperature >= 25 && fanstate == 0){
    sendIR(onoffFan,signal_len);
    fanstate = 1;
  }else if (temperature < 25 && fanstate == 1){
    sendIR(onoffFan,signal_len);
    fanstate = 0;
  }
}

void switchIRSignal(){
  // Set modeButtonState depending upon switch position
  modeButtonState = digitalRead(modePin);
  // If the button is pressed, send ir signals
  if (modeButtonState == HIGH){
    currentMode = currentMode + 1;
    if (currentMode >= 3){
      currentMode = 0;
    }
    Serial.print("switch to ");
    Serial.println(currentMode);
  }
}

String command;

void sendIRByCommand(){
  while(Serial.available()) {
    command= Serial.readString();// read the incoming data as string
    Serial.println(command);
    for (int i = 0 ; i < TOTAL_SIGNALS; i++){
      bool flag = true;
      for (int j = 0; j < signals[i].command.length(); j++)
        if (signals[i].command[j] != command[j]){
          flag = false;
          break;
        }
      if (flag){
        sendIR(signals[i].ir_wave, signals[i].ir_size);
        break;
      }
    }
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  //readEnvironment(1);
  //decodeIR();
  sendIRByCommand();
  //sendIRByButton(modeList[currentMode],signal_len);
  //switchIRSignal();
  //automatic_control();
  //delay(500);
}
