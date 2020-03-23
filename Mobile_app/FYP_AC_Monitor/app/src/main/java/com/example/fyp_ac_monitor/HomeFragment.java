package com.example.fyp_ac_monitor;

import android.os.Bundle;
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

public class HomeFragment extends Fragment {

    MenuActivity activity;
    Button _feedback_popup_button;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {

        activity = (MenuActivity) getActivity();
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
                        return true;
                    }
                });

                popup.show();
            }
        });

        return show_view;
    }

}
