package com.example.fyp_ac_monitor.activity;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;

import android.os.Bundle;
import android.view.MenuItem;
import android.widget.Toast;

import com.example.fyp_ac_monitor.ChartFragment;
import com.example.fyp_ac_monitor.ControlFragment;
import com.example.fyp_ac_monitor.HomeFragment;

import com.example.fyp_ac_monitor.R;

import com.google.android.material.bottomnavigation.BottomNavigationView;

public class MenuActivity extends AppCompatActivity {



    public int current_fragment_id;
    public String feed_back_button_title;


    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_menu);

        feed_back_button_title = getResources().getString(R.string.home_fragment_feedback_default);

        BottomNavigationView bottomNav = findViewById(R.id.bottom_navigation_bar);

        bottomNav.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(@NonNull MenuItem menuItem) {
                Fragment selectedFragment = null;
                current_fragment_id = menuItem.getItemId();
                switch (menuItem.getItemId()){
                    case R.id.nav_home:
                        selectedFragment = new HomeFragment();
                        break;
                    case R.id.nav_chart:
                        selectedFragment = new ChartFragment();
                        break;
                    case R.id.nav_control:
                        selectedFragment = new ControlFragment();
                        break;
                }

                getSupportFragmentManager().beginTransaction().replace(R.id.fragment_container, selectedFragment).commit();

                return true;
            }
        });

        getSupportFragmentManager().beginTransaction().replace(R.id.fragment_container, new HomeFragment()).commit();

    }
}
