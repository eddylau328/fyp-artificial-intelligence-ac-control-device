#include <PZEM004Tv30.h>

PZEM004Tv30 pzem(&Serial3);

String send_command = "ping";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  Serial.println("Reset Energy");
  pzem.resetEnergy();

  Serial.println("Set address to 0x42");
  pzem.setAddress(0x42);
  
}

void readSerialCommand(){
  String command = "";
  while (Serial.available()){
    char ch = Serial.read();
    command += ch;
  }
  for (int i = command.length()-1; i > 0 ; i--){
    if (command[i] == '\n' or command[i] == '\r'){
      command[i] = '\0';
      break;
    }
  }

  bool flag = true;
  for (int i = 0; i < command.length(); i++){
    if (command[i] != send_command[i]){
      flag = false;
      break;
    }
  }
  if (flag == true){
    Serial.println("pong");
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0){
    readSerialCommand();
  }

  float volt = pzem.voltage();
  Serial.print("Voltage: ");
  Serial.print(volt);
  Serial.println("V");

  float cur = pzem.current();
  Serial.print("Current: ");
  Serial.print(cur);
  Serial.println("A");

  float powe = pzem.power();
  Serial.print("Power: ");
  Serial.print(powe);
  Serial.println("W");

  float ener = pzem.energy();
  Serial.print("Energy: ");
  Serial.print(ener,3);
  Serial.println("kWh");

  float freq = pzem.frequency();
  Serial.print("Frequency: ");
  Serial.print(freq);
  Serial.println("Hz");

  float pf = pzem.pf();
  Serial.print("PF: ");
  Serial.println(pf);

  delay(1000);
}
