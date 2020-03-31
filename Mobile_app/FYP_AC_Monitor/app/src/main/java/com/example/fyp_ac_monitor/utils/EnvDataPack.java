package com.example.fyp_ac_monitor.utils;

public class EnvDataPack {

    public long stepNo;
    public String feedback;
    public long temp;
    public long hum;
    public long outdoor_temp;
    public long outdoor_hum;
    public String time;

    public EnvDataPack() {
    }

    public EnvDataPack(long stepNo, String feedback, long temp, long hum, long outdoor_temp, long outdoor_hum, String time) {
        this.stepNo = stepNo;
        this.feedback = feedback;
        this.temp = temp;
        this.hum = hum;
        this.outdoor_temp = outdoor_temp;
        this.outdoor_hum = outdoor_hum;
        this.time = time;
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

    public long getTemp() {
        return temp;
    }

    public void setTemp(long temp) {
        this.temp = temp;
    }

    public long getHum() {
        return hum;
    }

    public void setHum(long hum) {
        this.hum = hum;
    }

    public long getOutdoor_temp() {
        return outdoor_temp;
    }

    public void setOutdoor_temp(long outdoor_temp) {
        this.outdoor_temp = outdoor_temp;
    }

    public long getOutdoor_hum() {
        return outdoor_hum;
    }

    public void setOutdoor_hum(long outdoor_hum) {
        this.outdoor_hum = outdoor_hum;
    }

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }
}
