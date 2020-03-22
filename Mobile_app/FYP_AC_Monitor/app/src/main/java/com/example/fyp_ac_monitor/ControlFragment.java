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

public class ControlFragment extends Fragment {

    Switch _powerSwitch;
    NumberPicker _tempPicker;
    NumberPicker _fanspeedPicker;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View show_view = inflater.inflate(R.layout.fragment_control, container, false);
        _powerSwitch = (Switch) show_view.findViewById(R.id.control_fragment_power_switch);
        _powerSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked == true){
                    Toast.makeText(getActivity(), "ON", Toast.LENGTH_SHORT).show();
                }else{
                    Toast.makeText(getActivity(), "OFF", Toast.LENGTH_SHORT).show();
                }
            }
        });

        _tempPicker = (NumberPicker) show_view.findViewById(R.id.control_fragment_temp_picker);
        _tempPicker.setMinValue(17);
        _tempPicker.setMaxValue(30);
        _tempPicker.setWrapSelectorWheel(false);

        _fanspeedPicker = (NumberPicker) show_view.findViewById(R.id.control_fragment_fanspeed_picker);
        _fanspeedPicker.setMinValue(1);
        _fanspeedPicker.setMaxValue(3);
        _fanspeedPicker.setWrapSelectorWheel(false);

        return show_view;
    }
}
