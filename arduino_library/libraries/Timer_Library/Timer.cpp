/*
  Timer.cpp - Library for counting time
  Created by Eddy Lau, January 18, 2020.
*/

#include "Arduino.h"
#include "Timer.h"

Timer::Timer(){}

void Timer::settimer(long interval){
    this->interval = interval;
}

// use to start a timer after setting / start after a pause
void Timer::starttimer(){
    // millis() <- arduino function, return current millisecond
    if (isPause == false){
        previousMillis = millis();
        isCounting = true;
    } else {
        unsigned long difference = pauseMillis - previousMillis;
        previousMillis = millis() - difference;
        isPause = false;
    }
}

void Timer::resettimer(){
    // if the timer is reset, isPause & isCounting are false
    // No matter it is pausing or counting
    isCounting = false;
    isPause = false;
}

void Timer::pausetimer(){
    // prevent multiple pausetimer() call
    // prevent pause even the timer is not yet started
    if (isPause == false && isCounting == true){
        isPause = true;
        pauseMillis = millis();
    }
}

// this method is needed to keep tracing
// put it inside void loop()
bool Timer::checkfinish(){
    if (!isCounting){
        return false;
    }
    unsigned long currentMillis = millis();
    if (isPause){
        currentMillis = pauseMillis;
    }
    // check the difference between starting time and the current time
    // if larger than the interval then finish counting, else not yet finish
    if (currentMillis - previousMillis > interval){
        return true;
    } else{
        return false;
    }
}

bool Timer::checkCounting(){
    return isCounting;
}

long int Timer::getInterval(){return interval;}
unsigned long Timer::getDelatTime(){
    if (!isCounting){
        return 0;
    }
    if (isPause){
        return millis()-previousMillis;
    }else{
        return pauseMillis-previousMillis;
    }
}
bool Timer::getTimerState(){return isCounting;}
bool Timer::getTimerPause(){return isPause;}
