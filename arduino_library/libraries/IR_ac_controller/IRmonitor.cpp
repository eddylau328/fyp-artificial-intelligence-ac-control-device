/*
  IRmonitor.h - Library for controlling the AC
  Created by Eddy Lau, March 17, 2020.
*/
#include "IRmonitor.h"
#include "Arduino.h"
#include <IRremote.h>

IRmonitor::IRmonitor(){}

bool IRmonitor::checkCommand(String input_command){
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
      if (value == 1 || value == 2 || value == 3 || value == 4)
        return true;
      else
        return false;
  }
  return false;
}

int IRmonitor::get_command(String input_command){
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

int IRmonitor::get_command_value(String input_command, int i){
  String value = "";
  if (i == 1 or i == 2){
    for (int j = commands[i].length(); j < input_command.length();j++){
      if (input_command[j] >= '0' && input_command[j] <= '9'){
        value += input_command[j];
      }else if (input_command[j] == ' ' && value.length() == 0){
        continue;
      }else{
        break;
      }
    }
    return value.toInt();
  }
  else if (i == 0){
    for (int j = commands[i].length(); j < input_command.length();j++){
      if (input_command[j] != ' ' && input_command[j] != '\0' && input_command[j] != '\n')
        value += input_command[j];
    }
    if (value == "on")
      return 1;
    else if (value == "off")
      return 0;
    else
      return -1;
  }else{
    return -1;
  }
}

void IRmonitor::sendCommand(IRrecv &irrecv, IRsend &irsend, String input_command){
  int command_num = get_command(input_command);
  int command_value = get_command_value(input_command, command_num);
  unsigned *send_wave = wave;

  switch(command_num){
    case 0:
      power_state = command_value;
      break;
    case 1:
      temperature = command_value;
      break;
    case 2:
      fanspeed = command_value;
      break;
  }

  if (power_state != 0){
    translate_signal(send_wave);
  }else{
    send_wave = off_wave;
  }
  sendIR(irrecv, irsend, send_wave, SIGNAL_LENGTH);
}

void IRmonitor::sendIR(IRrecv &irrecv, IRsend &irsend, unsigned int raw[], int rawlen) {
  irsend.sendRaw(raw, rawlen, 38);
  Serial.println("send");
  // Enable the ir receiver
  irrecv.enableIRIn();
}

void IRmonitor::translate_signal(unsigned int *send_wave){
  for (int i=1; i<15;i++){
    if (temp_mask[i][0] == temperature){
      assign_mask_value(send_wave, temp_mask[0], temp_mask[i], 9);
      break;
    }
  }
  for (int i=1; i<5;i++){
    if (fanspeed_mask[i][0] == fanspeed){
      assign_mask_value(send_wave, fanspeed_mask[0], fanspeed_mask[i], 7);
      break;
    }
  }
  for (int i=1; i<3;i++){
    if (power_mask[i][0] == power_state){
      assign_mask_value(send_wave, power_mask[0], power_mask[i], 3);
      break;
    }
  }
}

void IRmonitor::assign_mask_value(unsigned int *send_wave, int mask_location[], int mask_value[], int mask_length){
  // first value is control function
  for (int i = 1; i < mask_length; i++)
    send_wave[mask_location[i]] = (mask_value[i])? high:low;
}
