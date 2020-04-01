package com.example.fyp_ac_monitor.utils;

public class EnvDataPack {

    public long stepNo;
    public String feedback;
    public double temp;
    public double hum;
    public double outdoor_temp;
    public double outdoor_hum;
    public String time;

    public EnvDataPack() {
    }

    public long getStepNo() {
        return stepNo;
    }

    public void setStepNo(long stepNo) {
        this.stepNo = stepNo;
    }

    public String getFeedback() {
        return feedback;
    }

    public void setFeedback(String feedback) {
        this.feedback = feedback;
    }

    public double getTemp() {
        return temp;
    }

    public void setTemp(double temp) {
        this.temp = temp;
    }

    public double getHum() {
        return hum;
    }

    public void setHum(double hum) {
        this.hum = hum;
    }

    public double getOutdoor_temp() {
        return outdoor_temp;
    }

    public void setOutdoor_temp(double outdoor_temp) {
        this.outdoor_temp = outdoor_temp;
    }

    public double getOutdoor_hum() {
        return outdoor_hum;
    }

    public void setOutdoor_hum(double outdoor_hum) {
        this.outdoor_hum = outdoor_hum;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

    public EnvDataPack(long stepNo, String feedback, double temp, double hum, double outdoor_temp, double outdoor_hum, String time) {
        this.stepNo = stepNo;
        this.feedback = feedback;
        this.temp = temp;
        this.hum = hum;
        this.outdoor_temp = outdoor_temp;
        this.outdoor_hum = outdoor_hum;
        this.time = time;
    }
}
