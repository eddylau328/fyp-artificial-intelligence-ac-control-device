package com.example.fyp_ac_monitor;

import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.PopupMenu;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.fyp_ac_monitor.activity.MenuActivity;
import com.example.fyp_ac_monitor.utils.EnvDataPack;
import com.example.fyp_ac_monitor.utils.PreferenceUtils;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class HomeFragment extends Fragment {

    MenuActivity activity;
    Button _feedback_popup_button;
    LineChart chart;

    MyFirebase db;
    String username;
    final ArrayList<Entry> entries = new ArrayList<>();

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        db = new MyFirebase();
        activity = (MenuActivity) getActivity();
        username = PreferenceUtils.loadUsername(activity);

        View show_view = inflater.inflate(R.layout.fragment_home, container, false);
        _feedback_popup_button = (Button) show_view.findViewById(R.id.home_fragment_feedback_popup_button);
        _feedback_popup_button.setText(activity.feed_back_button_title);
        _feedback_popup_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                PopupMenu popup = new PopupMenu(activity, v);
                popup.getMenuInflater().inflate(R.menu.feedback_popup_menu, popup.getMenu());
                popup.setOnMenuItemClickListener(new PopupMenu.OnMenuItemClickListener() {
                    @Override
                    public boolean onMenuItemClick(MenuItem item) {
                        activity.feed_back_button_title = String.valueOf(item.getTitle());
                        _feedback_popup_button.setText(activity.feed_back_button_title);
                        Toast.makeText(activity, "You Clicked " + activity.feed_back_button_title, Toast.LENGTH_SHORT).show();

                        db.sendFeedback(username, activity.feed_back_button_title);

                        return true;
                    }
                });

                popup.show();
            }
        });

        chart = (LineChart) show_view.findViewById(R.id.home_fragment_linechart);
        chart.setDragEnabled(false);
        chart.setScaleEnabled(true);

        db.getEnvData(username, new MyFirebase.envData_callBack() {
            @Override
            public void onCallBack_dataIsLoaded(List<EnvDataPack> dataPacks, List<String> keys) {
                for (EnvDataPack dataPack: dataPacks) {
                    entries.add(new Entry(dataPack.getStepNo(), dataPack.getTemp()));
                }
                Toast.makeText(activity,String.valueOf(entries.size()), Toast.LENGTH_SHORT).show();
                LineDataSet set = new LineDataSet(entries, "Temperature");
                List<ILineDataSet> dataSets = new ArrayList<>();
                dataSets.add(set);
                LineData data = new LineData(dataSets);
                chart.setData(data);
                chart.invalidate(); // refresh
            }
        });

        return show_view;
    }

}
