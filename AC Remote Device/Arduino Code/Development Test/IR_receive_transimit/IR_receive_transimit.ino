#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_HTU21DF.h>
#include <BH1750.h>
#include <avr/pgmspace.h>
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

#define TOTAL_SIGNALS 16
#define SIGNAL_LENGTH 100

class IRsignal{
  public:
    String command;
    int pos;
    // constructor
    IRsignal(){}
    // constructor
    IRsignal(String command, int pos){
      create(command, pos);
    }
    
    void create(String command, int pos){
      this->command = command;
      this->pos = pos;
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

/*
Commands
- "power on"
- "power off"
- "temp <deg C>" ~(deg C) is within [17,25]
- "fanspeed <level>"  ~(level) is within [1,3]
- "fanspeed auto"
- "mode"
- "swing on"
- "swing off"
- "economy on"
- "economy off"
*/
#define POWER_ON 0
#define POWER_OFF 1
#define FANSPEED_1 2
#define FANSPEED_2 3
#define FANSPEED_3 4
#define TEMP_25 5
#define TEMP_24 6
#define TEMP_23 7
#define TEMP_22 8
#define TEMP_21 9
#define TEMP_20 10
#define TEMP_19 11
#define TEMP_18 12
#define TEMP_17 13 
#define SWING 14
#define SWING_ON 14
#define SWING_OFF 15
 
const static uint16_t power_on[] PROGMEM = {4450,4250,600,1550,650,450,650,1500,600,1600,600,450,600,500,600,1550,600,500,600,450,600,1600,550,500,600,500,600,1550,600,1550,600,500,650,1500,600,1550,650,450,600,1550,700,1500,600,1550,600,1550,550,1600,650,1500,600,500,600,1550,600,500,600,450,650,450,600,500,600,450,650,450,600,500,550,1600,600,500,600,450,650,450,600,500,600,450,650,450,600,1550,650,450,550,1600,600,1550,600,1600,600,1550,650,1500,600,1550,500};
const static uint16_t power_off[] PROGMEM = {4300,4400,600,1550,650,450,600,1550,600,1550,600,500,600,450,650,1550,600,450,600,500,650,1500,600,500,600,500,600,1550,600,1550,600,500,600,1550,650,450,600,1550,600,1550,650,1500,650,1500,600,500,600,1550,700,1500,600,1550,650,450,600,450,650,450,600,450,650,1550,600,450,650,450,650,1500,700,1500,600,1550,600,450,650,450,650,450,600,450,700,400,650,450,600,450,650,450,650,1500,600,1600,600,1550,600,1550,600,1550,500};
const static uint16_t fanspeed_1[] PROGMEM = {4400,4350,600,1550,550,500,600,1600,600,1550,600,450,600,500,600,1550,600,500,600,500,550,1600,550,500,600,500,600,1550,600,1550,600,500,600,1550,600,1600,600,450,600,500,600,1550,600,1550,600,1550,600,1600,600,1550,600,450,600,1600,550,1600,550,500,600,500,600,500,600,450,600,500,550,550,600,1550,600,500,600,450,600,500,600,500,550,500,600,500,600,1550,600,500,600,1550,600,1550,600,1550,600,1600,600,1550,550,1600,550};
const static uint16_t fanspeed_2[] PROGMEM = {4450,4250,650,1550,600,450,600,1600,600,1550,600,450,600,500,600,1550,650,450,600,500,600,1550,600,500,600,450,600,1550,600,1600,600,450,600,1550,600,500,600,1550,600,500,600,1550,600,1550,600,1600,600,1550,600,1550,600,1550,600,500,600,1550,600,500,600,450,600,500,600,500,600,450,600,500,600,1550,600,500,600,500,550,500,600,500,600,500,600,450,600,1600,600,450,600,1600,600,1550,600,1550,600,1550,600,1550,600,1550,550};
const static uint16_t fanspeed_3[] PROGMEM = {4400,4300,600,1550,600,500,600,1550,600,1550,600,500,550,550,600,1550,600,450,600,500,600,1550,600,500,600,500,600,1550,600,1550,650,450,600,1550,600,500,600,450,600,1550,600,1600,600,1550,600,1550,600,1550,600,1550,600,1600,600,1550,600,450,600,500,600,500,600,450,600,500,550,550,550,500,600,1600,550,500,600,500,550,500,600,500,600,500,600,450,600,1600,600,450,600,1600,600,1550,550,1600,600,1550,600,1550,600,1550,550};
const static uint16_t temp_25[] PROGMEM = {4400,4300,650,1500,650,450,600,1550,650,1500,600,500,600,500,600,1550,600,500,600,450,600,1550,650,450,600,500,600,1550,550,1600,600,500,600,1550,650,450,600,450,600,1600,600,1550,600,1550,600,1550,650,1500,650,1500,600,1600,600,1550,600,500,600,450,600,500,600,450,650,450,600,500,600,1550,600,1550,650,450,600,500,600,450,650,450,600,500,600,450,600,500,650,450,600,1550,600,1550,600,1550,650,1500,600,1600,600,1550,500};
const static uint16_t temp_24[] PROGMEM = {4450,4250,600,1550,600,500,650,1500,600,1550,600,500,600,500,600,1550,600,500,600,450,600,1600,600,450,600,500,600,1550,600,1550,650,450,600,1550,600,500,600,500,550,1600,600,1550,600,1550,600,1550,600,1600,600,1550,600,1550,650,1500,600,500,600,450,600,500,650,450,600,450,600,500,600,500,600,1550,650,450,600,450,650,450,600,500,600,450,600,500,600,1550,600,500,650,1500,650,1500,600,1600,600,1550,600,1550,600,1550,500};
const static uint16_t temp_23[] PROGMEM = {4450,4250,600,1600,600,450,650,1500,700,1500,600,450,600,500,600,1550,650,450,600,450,650,1550,550,500,650,450,600,1550,600,1550,650,450,600,1550,600,500,650,1500,600,500,650,1500,600,1550,650,1500,600,1600,600,1550,550,1600,650,450,600,1550,600,500,600,450,600,500,600,500,600,450,650,450,550,1600,600,500,550,1600,600,500,600,450,600,500,650,450,600,1550,600,500,600,1550,550,550,550,1600,600,1550,600,1550,600,1550,550};
const static uint16_t temp_22[] PROGMEM = {4450,4250,650,1550,600,450,650,1500,700,1500,650,400,650,450,600,1550,650,450,600,450,650,1550,600,450,600,500,650,1500,650,1500,650,450,600,1550,600,500,650,450,600,1550,600,1550,650,1500,650,1500,650,1500,650,1550,600,1550,600,1550,600,500,600,450,700,400,600,500,600,450,650,450,650,450,600,1550,650,1500,600,1550,650,450,650,450,650,400,650,450,600,1550,600,500,600,450,650,450,600,1550,650,1500,650,1550,600,1550,500};
const static uint16_t temp_21[] PROGMEM = {4500,4200,650,1550,650,400,600,1550,650,1550,600,450,650,450,600,1550,650,450,600,450,650,1550,600,450,700,400,650,1500,650,1500,700,400,700,1450,650,450,650,450,650,1500,600,1550,650,1500,650,1500,600,1600,600,1550,650,1500,650,1500,650,450,600,500,650,400,650,450,600,500,600,450,600,500,600,1550,650,1500,700,400,600,500,650,400,700,400,600,500,600,1550,600,450,650,450,600,1550,650,1500,650,1550,600,1550,600,1550,500};
const static uint16_t temp_20[] PROGMEM = {4350,4350,600,1550,600,500,600,1550,600,1550,600,500,600,450,600,1550,650,450,600,500,600,1550,650,450,600,450,600,1600,600,1550,650,400,600,1600,600,450,650,450,600,1550,650,1500,650,1550,600,1550,600,1550,600,1550,600,1550,600,1550,650,450,600,500,550,500,650,450,600,500,600,450,600,500,600,500,600,1550,600,500,600,450,600,500,600,500,600,450,600,1550,650,1550,550,500,600,1550,650,1550,600,1550,600,1550,600,1550,500};
const static uint16_t temp_19[] PROGMEM = {4450,4250,700,1500,650,400,650,1550,650,1500,600,450,700,400,650,1500,650,450,700,400,600,1550,600,500,650,400,650,1500,700,1450,650,450,650,1500,700,400,700,400,650,1500,650,1500,650,1500,650,1550,600,1550,650,1500,600,1550,650,1500,700,400,650,450,600,450,650,450,650,450,650,400,700,400,650,450,650,1500,600,1550,700,400,650,400,700,400,650,450,650,1500,650,1500,650,450,700,400,650,1500,650,1500,650,1500,650,1500,500};
const static uint16_t temp_18[] PROGMEM = {4300,4400,600,1550,600,450,650,1550,600,1550,600,450,550,550,550,1600,600,500,600,500,600,1550,600,500,550,500,600,1550,650,1500,650,450,600,1550,600,500,500,600,600,1550,600,1550,600,1550,600,1550,650,1550,600,1550,600,1550,600,1550,550,550,600,500,600,450,600,500,600,450,600,500,600,500,600,500,550,500,650,1500,600,500,550,550,600,450,650,450,550,1600,600,1550,600,1600,600,450,600,1550,600,1600,600,1550,600,1550,500};
const static uint16_t temp_17[] PROGMEM = {4400,4300,600,1550,600,500,600,1550,600,1600,550,500,600,500,600,1550,600,500,600,450,600,1600,600,450,600,500,600,1550,600,1550,600,500,650,1500,600,500,600,500,550,1600,600,1550,600,1550,600,1550,600,1600,550,1600,600,1550,600,1550,600,500,600,500,600,450,600,500,600,500,600,450,650,450,600,500,550,500,600,500,600,500,600,450,650,450,600,500,600,1550,600,1550,600,1550,650,1500,600,1550,600,1600,600,1550,550,1600,550};
const static uint16_t swing[] PROGMEM = {4400,4300,600,1550,600,500,600,1550,600,1550,650,450,600,450,600,1600,600,450,650,450,600,1550,600,500,600,500,600,1550,550,1600,600,500,600,1550,550,550,600,450,650,450,600,450,650,1550,600,1550,600,1550,600,1550,600,1600,550,1600,600,1550,600,1550,600,500,550,500,600,500,600,500,600,1550,600,1550,600,1550,650,450,600,500,600,450,600,500,600,500,600,450,650,450,600,500,600,1550,600,1550,600,1550,600,1600,550,1600,500};

const static uint16_t *const signals_table[] PROGMEM = {power_on, power_off, fanspeed_1, fanspeed_2, fanspeed_3, temp_25,temp_24,temp_23,temp_22,temp_21,temp_20,temp_19,temp_18,temp_17,swing};


class IRmonitor{
  public:
    int fan_state = 1;
    int temperature = 24;
    int swing_on = 0;
    const int fan_speed_amplitude[4][6] = {{35,37,39,51,53,55},{1,0,0,0,1,1},{0, 1, 0, 1, 0, 1},{0, 0, 1, 1, 1, 0}};
    const int high = 1550;
    const int low = 500;
    IRsignal *signals;

    /*
     *      35,37,39,51,53,55
     * low   1, 0, 0, 0, 1, 1
     * med   0, 1, 0, 1, 0, 1
     * high  0, 0, 1, 1, 1, 0
     */

    IRmonitor(){}
    void create(IRsignal *signals){
      this->signals = signals;
    }
    
    bool checkCommand(String input_command){
      // remove input command possible enter character
      for (int i = input_command.length() - 1; i >= 0; i++)
        if (input_command[i] == "\n"){
          input_command[i] = "\0";
          break;
        }
      bool flag = false;
      for (int i = 0 ; i < TOTAL_SIGNALS; i++){
        flag = false;
        if (input_command.length() == signals[i].command.length()){
          flag = true;
          for (int j = 0; j < input_command.length(); j++){
            if (signals[i].command[j] != input_command[j]){
              flag = false;
              break;
            }
          }
          if (flag == true){
            return true;
          }
        }
      }
      return false;
    }

    bool sendCommand(IRrecv &irrecv, IRsend &irsend, String input_command){
      for (int i = input_command.length() - 1; i >= 0; i++)
        if (input_command[i] == "\n"){
          input_command[i] = "\0";
          break;
        }
      bool flag = false;
      for (int i = 0 ; i < TOTAL_SIGNALS; i++){
        flag = false;
        if (input_command.length() == signals[i].command.length()){
          flag = true;
          for (int j = 0; j < input_command.length(); j++){
            if (signals[i].command[j] != input_command[j]){
              flag = false;
              break;
            }
          }
          if (flag == true){
            unsigned int wave[SIGNAL_LENGTH];
            switch (signals[i].pos){
              case POWER_ON:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[POWER_ON]+k);
                break;
              case POWER_OFF:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[POWER_OFF]+k);
                break;
              case FANSPEED_1:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[FANSPEED_1]+k);
                break;
              case FANSPEED_2:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[FANSPEED_2]+k);
                break;
              case FANSPEED_3:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[FANSPEED_3]+k);
                break;
              case TEMP_25:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_25]+k);
                break;
              case TEMP_24:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_24]+k);
                break;
              case TEMP_23:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_23]+k);
                break;
              case TEMP_22:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_22]+k);
                break;
              case TEMP_21:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_21]+k);
                break;
              case TEMP_20:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_20]+k);
                break;
              case TEMP_19:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_19]+k);
                break;
              case TEMP_18:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_18]+k);
                break;
              case TEMP_17:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[TEMP_17]+k);
                break;
              case SWING_ON:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[SWING]+k);
                break;
              case SWING_OFF:
                for (int k = 0; k < SIGNAL_LENGTH; k++)
                  wave[k] = pgm_read_word(signals_table[SWING]+k);
                break;
            }
            sendIR(irrecv, irsend, wave, SIGNAL_LENGTH);
          }
        }
      }
    }
    
    void sendIR(IRrecv &irrecv, IRsend &irsend, unsigned int raw[], int rawlen) {
      irsend.sendRaw(raw, rawlen, 38);
      Serial.println("send");
      // Enable the ir receiver
      irrecv.enableIRIn();
    }
};


IRmonitor ir_monitor;
IRsignal signals[TOTAL_SIGNALS];

void IRsignals_command_setup(){
  signals[0].create("power on", POWER_ON);
  signals[1].create("power off", POWER_OFF);
  signals[2].create("fanspeed 1", FANSPEED_1);
  signals[3].create("fanspeed 2", FANSPEED_2);
  signals[4].create("fanspeed 3", FANSPEED_3);
  signals[5].create("temp 25", TEMP_25);
  signals[6].create("temp 24", TEMP_24);
  signals[7].create("temp 23", TEMP_23);
  signals[8].create("temp 22", TEMP_22);
  signals[9].create("temp 21", TEMP_21);
  signals[10].create("temp 20", TEMP_20);
  signals[11].create("temp 19", TEMP_19);
  signals[12].create("temp 18", TEMP_18);
  signals[13].create("temp 17", TEMP_17);
  signals[14].create("swing on", SWING);
  signals[15].create("swing off", SWING);
  
  ir_monitor.create(signals);
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

String command;

void sendIRByCommand(){
  while(Serial.available()) {
    command= Serial.readString();// read the incoming data as string
    Serial.print(command);
    if (ir_monitor.checkCommand(command))
      ir_monitor.sendCommand(irrecv, irsend, command);
    /*
    for (int i = 0 ; i < TOTAL_SIGNALS; i++){
      bool flag = true;
      for (int j = 0; j < signals[i].command.length(); j++)
        if (signals[i].command[j] != command[j]){
          flag = false;
          break;
        }
      if (flag){
        unsigned int wave[SIGNAL_LENGTH];
        switch (signals[i].pos){
          case POWER_ON:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[POWER_ON]+k);
            break;
          case POWER_OFF:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[POWER_OFF]+k);
            break;
          case FANSPEED_1:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[FANSPEED_1]+k);
            break;
          case FANSPEED_2:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[FANSPEED_2]+k);
            break;
          case FANSPEED_3:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[FANSPEED_3]+k);
            break;
          case TEMP_25:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_25]+k);
            break;
          case TEMP_24:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_24]+k);
            break;
          case TEMP_23:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_23]+k);
            break;
          case TEMP_22:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_22]+k);
            break;
          case TEMP_21:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_21]+k);
            break;
          case TEMP_20:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_20]+k);
            break;
          case TEMP_19:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_19]+k);
            break;
          case TEMP_18:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_18]+k);
            break;
          case TEMP_17:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[TEMP_17]+k);
            break;
          case SWING_ON:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[SWING]+k);
            break;
          case SWING_OFF:
            for (int k = 0; k < SIGNAL_LENGTH; k++)
              wave[k] = pgm_read_word(signals_table[SWING]+k);
            break;
        }
        sendIR(wave, SIGNAL_LENGTH);
        break;
      }
    }
    */
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  // readEnvironment(1);
  decodeIR();
  //sendIRByCommand();
  //sendIRByButton(modeList[currentMode],signal_len);
  delay(500);
}
