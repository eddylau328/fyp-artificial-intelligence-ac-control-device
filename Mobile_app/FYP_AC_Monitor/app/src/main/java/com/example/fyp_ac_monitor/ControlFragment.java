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
import com.example.fyp_ac_monitor.activity.MenuActivity;

import com.example.fyp_ac_monitor.utils.PreferenceUtils;

public class ControlFragment extends Fragment {

    String username;

    Switch _powerSwitch;
    NumberPicker _tempPicker;
    NumberPicker _fanspeedPicker;
    int previous_temp = 24;
    int previous_fanspeed = 1;
    boolean previous_power_state = false;
    boolean isDefaultCheck = true;

    MenuActivity activity;
    int fragment_id;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        activity = (MenuActivity) getActivity();
        username = PreferenceUtils.loadUsername(activity);
        fragment_id = R.id.nav_control;
        if (isDefaultCheck && activity.current_fragment_id == fragment_id)
            updateToACstatus(username);

        View show_view = inflater.inflate(R.layout.fragment_control, container, false);

        _powerSwitch = (Switch) show_view.findViewById(R.id.control_fragment_power_switch);
        if (isDefaultCheck)
            _powerSwitch.setEnabled(false);
        _powerSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (!isDefaultCheck) {
                    if (isChecked == true) {
                        activity.send_control_count_down_timer.cancel();
                        activity.send_control_count_down_timer.start();
                        activity.ac_power_state = true;
                        Toast.makeText(getActivity(), "ON", Toast.LENGTH_SHORT).show();
                    } else {
                        activity.send_control_count_down_timer.cancel();
                        activity.send_control_count_down_timer.start();
                        activity.ac_power_state = false;
                        Toast.makeText(getActivity(), "OFF", Toast.LENGTH_SHORT).show();
                    }
                }
            }
        });

        _tempPicker = (NumberPicker) show_view.findViewById(R.id.control_fragment_temp_picker);
        if (isDefaultCheck)
            _tempPicker.setEnabled(false);
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
                        activity.send_control_count_down_timer.cancel();
                        activity.send_control_count_down_timer.start();
                        Toast.makeText(getActivity(), String.valueOf(_tempPicker.getValue()), Toast.LENGTH_SHORT).show();
                        previous_temp = _tempPicker.getValue();
                        activity.ac_set_temp = _tempPicker.getValue();
                    }
                }
            }
        });

        _fanspeedPicker = (NumberPicker) show_view.findViewById(R.id.control_fragment_fanspeed_picker);
        if (isDefaultCheck)
            _fanspeedPicker.setEnabled(false);
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
                        activity.send_control_count_down_timer.cancel();
                        activity.send_control_count_down_timer.start();
                        Toast.makeText(getActivity(), String.valueOf(_fanspeedPicker.getValue()), Toast.LENGTH_SHORT).show();
                        previous_fanspeed = _fanspeedPicker.getValue();
                        activity.ac_set_fanspeed = _fanspeedPicker.getValue();
                    }
                }
            }
        });

        return show_view;
    }

    public void updateToACstatus(final String username){
        activity.db.getACstatus(username, new MyFirebase.ac_status_callback() {
            @Override
            public void onCallback_getACstatus(boolean power_state, int set_temp, int set_fanspeed) {
                if (power_state != _powerSwitch.isChecked()) {
                    previous_power_state = power_state;
                }
                if (set_temp != _tempPicker.getValue()){
                    previous_temp = set_temp;
                }
                if (set_fanspeed != _fanspeedPicker.getValue()){
                    previous_fanspeed = set_fanspeed;
                }

                if (_powerSwitch.isEnabled() == false) {
                    _powerSwitch.setEnabled(true);
                    _powerSwitch.setChecked(previous_power_state);
                    activity.ac_power_state = previous_power_state;
                }
                if (_tempPicker.isEnabled() == false) {
                    _tempPicker.setEnabled(true);
                    _tempPicker.setValue(previous_temp);
                    activity.ac_set_temp = previous_temp;
                }
                if (_fanspeedPicker.isEnabled() == false) {
                    _fanspeedPicker.setEnabled(true);
                    _fanspeedPicker.setValue(previous_fanspeed);
                    activity.ac_set_fanspeed = previous_fanspeed;
                }

                isDefaultCheck = false;
            }
        });
    }
}
