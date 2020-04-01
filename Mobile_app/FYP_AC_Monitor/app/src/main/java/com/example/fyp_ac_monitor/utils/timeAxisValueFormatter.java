package com.example.fyp_ac_monitor.utils;

import com.github.mikephil.charting.components.AxisBase;
import com.github.mikephil.charting.formatter.IAxisValueFormatter;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

public class timeAxisValueFormatter implements IAxisValueFormatter {

    private String[] mValues;
    SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
    SimpleDateFormat outputFormat = new SimpleDateFormat("HH:mm");

    public timeAxisValueFormatter(String[] values) {
        this.mValues = values;
    }

    @Override
    public String getFormattedValue(float value, AxisBase axis) {
        // "value" represents the position of the label on the axis (x or y)
        String date = null;
        try {
            date = outputFormat.format(dateFormat.parse(mValues[(int) value]));
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return date;
    }

}