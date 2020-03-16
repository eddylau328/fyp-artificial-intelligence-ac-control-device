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


class IRmonitor{
  public:
    int fan_state = 1;
    int temperature = 24;
    int swing_on = 0;
    unsigned int wave[SIGNAL_LENGTH] = {4450,4250,600,1550,650,450,650,1500,600,1600,600,450,600,500,600,1550,600,500,600,450,600,1600,550,500,600,500,600,1550,600,1550,600,500,650,1500,600,1550,650,450,600,1550,700,1500,600,1550,600,1550,550,1600,650,1500,600,500,600,1550,600,500,600,450,650,450,600,500,600,450,650,450,600,500,550,1600,600,500,600,450,650,450,600,500,600,450,650,450,600,1550,650,450,550,1600,600,1550,600,1600,600,1550,650,1500,600,1550,500};
    const int fanspeed_mask[4][7] = {{-1,35,37,39,51,53,55},
                                     {1,1,0,0,0,1,1},
                                     {2,0,1,0,1,0,1},
                                     {3,0,0,1,1,1,0}};
    const int temp_mask[15][9] = {{-1,67,69,71,73,83,85,87,89},
                                  {30,1,0,1,1,0,1,0,0},
                                  {29,1,0,1,0,0,1,0,1},
                                  {28,1,0,0,0,0,1,1,1},
                                  {27,1,0,0,1,0,1,1,0},
                                  {26,1,1,0,1,0,0,1,0},
                                  {25,1,1,0,0,0,0,1,1},
                                  {24,0,1,0,0,1,0,1,1},
                                  {23,0,1,0,1,1,0,1,0},
                                  {22,0,1,1,1,1,0,0,0},
                                  {21,0,1,1,0,1,0,0,1},
                                  {20,0,0,1,0,1,1,0,1},
                                  {19,0,0,1,1,1,1,0,0},
                                  {18,0,0,0,1,1,1,1,0},
                                  {17,0,0,0,0,1,1,1,1}};
    // 1: swing on, 0: swing off
    const int swing_mask[3][3] = {{-1,41,57},
                                  {1,0,1},
                                  {0,1,0}};
    // 1: power on, 0: power off
    const int power_mask[3][3] = {{-1,45,61},
                                  {1,1,0},
                                  {0,0,1}};
    // 0: cool mode
    const int mode_mask[2][5] = {{-1,75,77,91,93},{0,0,0,1,1}};
    const int high = 1550;
    const int low = 500;
    const String commands[4] = {{"power"},{"temp"},{"swing"},{"fanspeed"}};

    IRmonitor(){}

    bool checkCommand(String input_command){
      int command_num = get_command(input_command);
      if (command_num == -1)
        return false;
      int value = get_command_value(input_command, command_num);
      switch(command_num){
        case 0:
          if (value == 0 || value == 1)
            return true;
          else
            return false;
        case 1:
          if (value <= 30 && value >= 17)
            return true;
          else
            return false;
        case 2:
          if (value == 0 || value == 1)
            return true;
          else
            return false;
        case 3:
          if (value == 1 || value == 2 || value == 3)
            return true;
          else
            return false;
      }
      return false;
    }

    int get_command(String input_command){
      bool flag = false;
      for (int i = 0; i < 4; i++){
        flag = true;
        // -1 is ignoring the null character
        for (int j = 0; j < commands[i].length()-1; j++){
          if (input_command[j] != commands[i][j]){
            flag = false;
            break;
          }
        }
        if (flag == true){
          return i;
        }
      }
      return -1;
    }

    int get_command_value(String input_command, int i){
      String value = "";
      for (int j = commands[i].length()-1; j < input_command.length();j++){
        if (input_command[i] >= '0' && input_command[i] <= '9'){
          value += input_command[i];
        }else if (input_command[i] == ' ' && value.length() == 0){
          continue;
        }else{
          break;
        }
      }
      return value.toInt();
    }
      
    void sendCommand(IRrecv &irrecv, IRsend &irsend, String input_command){
      sendIR(irrecv, irsend, wave, SIGNAL_LENGTH);
    }
    
    void sendIR(IRrecv &irrecv, IRsend &irsend, unsigned int raw[], int rawlen) {
      irsend.sendRaw(raw, rawlen, 38);
      Serial.println("send");
      // Enable the ir receiver
      irrecv.enableIRIn();
    }

    private:
      void translate_signal(){
        for (int i=0; i<15;i++){
          if (temp_mask[i][0] == temperature){
            
          }
        }
      }

      void assign_mask_value(){
        
      }

};


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
    // remove input command possible enter character
    for (int i = command.length() - 1; i >= 0; i++)
      if (command[i] == "\n"){
        command[i] = "\0";
        break;
      }
    if (ir_monitor.checkCommand(command))
      ir_monitor.sendCommand(irrecv, irsend, command);
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
