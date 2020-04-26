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
import com.example.fyp_ac_monitor.utils.timeAxisValueFormatter;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.formatter.IAxisValueFormatter;
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;

import java.text.ParseException;
import java.text.ParsePosition;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class HomeFragment extends Fragment {

    MenuActivity activity;
    Button _feedback_popup_button;
    LineChart chart;

    MyFirebase db;
    String username;
    final ArrayList<Entry> entries = new ArrayList<>();
    SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSSSSS");

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
        chart.setDragEnabled(true);
        chart.setScaleEnabled(true);
        chart.getDescription().setEnabled(false);
        chart.setNoDataText("Air Conditioner is not turn on. No data available");
        db.getEnvData(username, new MyFirebase.envData_callBack() {
            @Override
            public void onCallBack_dataIsLoaded(List<EnvDataPack> dataPacks, List<String> keys, Boolean success) {
                if (success) {
                    int count = 0;
                    long temp = dataPacks.get(dataPacks.size() - 1).getStepNo();
                    for (int i = dataPacks.size() - 1; i > 0; i--) {
                        if (dataPacks.get(i).getStepNo() == 0) {
                            count = i;
                            break;
                        }
                        if (temp - dataPacks.get(i).getStepNo() >= 120) {
                            count = i;
                            break;
                        }
                    }
                    String[] date_str = new String[dataPacks.size() - count];
                    for (int i = count; i < dataPacks.size(); i++) {
                        date_str[i - count] = dataPacks.get(i).getTime();
                        entries.add(new Entry((float) (i - count), (float) dataPacks.get(i).getTemp()));
                    }
                    Toast.makeText(activity, date_str[0], Toast.LENGTH_SHORT).show();
                    LineDataSet set = new LineDataSet(entries, "Indoor Temperature");
                    LineData data = new LineData(set);

                    chart.setData(data);

                    XAxis xAxis = chart.getXAxis();
                    xAxis.setValueFormatter(new timeAxisValueFormatter(date_str));
                    chart.invalidate(); // refresh
                }
            }
        });

        return show_view;
    }

}
