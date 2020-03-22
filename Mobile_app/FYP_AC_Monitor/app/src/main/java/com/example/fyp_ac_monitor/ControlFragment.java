package com.example.fyp_ac_monitor;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CompoundButton;
import android.widget.NumberPicker;
import android.widget.Switch;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.fyp_ac_monitor.utils.PreferenceUtils;

public class ControlFragment extends Fragment {

    Switch _powerSwitch;
    NumberPicker _tempPicker;
    NumberPicker _fanspeedPicker;
    int previous_temp = 24;
    int previous_fanspeed = 1;

    private MyFirebase db;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View show_view = inflater.inflate(R.layout.fragment_control, container, false);

        _powerSwitch = (Switch) show_view.findViewById(R.id.control_fragment_power_switch);

        _powerSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked == true){
                    String save_username = PreferenceUtils.loadUsername(getActivity());
                    sendControlCommand(save_username, "power", "on");
                    Toast.makeText(getActivity(), "ON", Toast.LENGTH_SHORT).show();
                }else{
                    String save_username = PreferenceUtils.loadUsername(getActivity());
                    sendControlCommand(save_username, "power", "off");
                    Toast.makeText(getActivity(), "OFF", Toast.LENGTH_SHORT).show();
                }
            }
        });

        _tempPicker = (NumberPicker) show_view.findViewById(R.id.control_fragment_temp_picker);
        _tempPicker.setMinValue(17);
        _tempPicker.setMaxValue(30);
        _tempPicker.setWrapSelectorWheel(false);
        _tempPicker.setOnLongPressUpdateInterval(10);
        _tempPicker.setValue(previous_temp);

        _tempPicker.setOnScrollListener(new NumberPicker.OnScrollListener() {
            @Override
            public void onScrollStateChange(NumberPicker view, int scrollState) {
                if (scrollState == SCROLL_STATE_IDLE){
                    if (previous_temp != _tempPicker.getValue()){
                        String save_username = PreferenceUtils.loadUsername(getActivity());
                        sendControlCommand(save_username, "temp", String.valueOf(_tempPicker.getValue()));
                        Toast.makeText(getActivity(), String.valueOf(_tempPicker.getValue()), Toast.LENGTH_SHORT).show();
                        previous_temp = _tempPicker.getValue();
                    }
                }
            }
        });

        _fanspeedPicker = (NumberPicker) show_view.findViewById(R.id.control_fragment_fanspeed_picker);
        _fanspeedPicker.setMinValue(1);
        _fanspeedPicker.setMaxValue(3);
        _fanspeedPicker.setWrapSelectorWheel(false);
        _fanspeedPicker.setOnLongPressUpdateInterval(10);
        _fanspeedPicker.setValue(previous_fanspeed);

        _fanspeedPicker.setOnScrollListener(new NumberPicker.OnScrollListener() {
            @Override
            public void onScrollStateChange(NumberPicker view, int scrollState) {
                if (scrollState == SCROLL_STATE_IDLE){
                    if (previous_fanspeed != _fanspeedPicker.getValue()){
                        String save_username = PreferenceUtils.loadUsername(getActivity());
                        sendControlCommand(save_username, "fanspeed", String.valueOf(_fanspeedPicker.getValue()));
                        Toast.makeText(getActivity(), String.valueOf(_fanspeedPicker.getValue()), Toast.LENGTH_SHORT).show();
                        previous_fanspeed = _fanspeedPicker.getValue();
                    }
                }
            }
        });

        db = new MyFirebase();

        return show_view;
    }

    public void sendControlCommand(final String username, final String function, final String value){
        String send_command = "ir " + function + " " + value;
        db.sendControlCommand(username, send_command);
    }
}
