/*
  Timer.h - Library for counting time
  Created by Eddy Lau, January 18, 2020.
*/
#ifndef Timer_h
#define Timer_h

#include "Arduino.h"

class Timer{
  private:
    // Generally, you should use "unsigned long" for variables that hold time
    // The value will quickly become too large for an int to store
    unsigned long previousMillis = 0;
    unsigned long pauseMillis = 0;
    long int interval = 0;
    bool isCounting = false;
    bool isPause = false;

  public:
    // Constructor
    // Create Timer
    Timer();
    // set the timer interval in milliseconds
    void settimer(long interval);
    // start counting
    void starttimer();
    // pause timer
    void pausetimer();
    // reset the counter, after reset you need to start again by calling the start function
    void resettimer();
    // check whether the timer is finish
    bool checkfinish();
    // get function
    // get the interval you set
    long int getInterval();
    // get the how much time has been counted so far
    unsigned long getDelatTime();
    // get the timer is counting or not
    // you can consider it to be whether the timer is on or off
    bool getTimerState();
    // get the timer is pausing or not
    bool getTimerPause();
};

#endif
