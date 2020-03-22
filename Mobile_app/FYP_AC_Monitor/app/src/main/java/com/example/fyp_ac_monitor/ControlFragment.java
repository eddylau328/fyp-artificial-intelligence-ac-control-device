package com.example.fyp_ac_monitor;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CompoundButton;
import android.widget.Switch;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

public class ControlFragment extends Fragment {

    Switch _powerSwitch;

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

        return show_view;
    }
}
