package com.example.fyp_ac_monitor.activity;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import com.example.fyp_ac_monitor.R;

public class MainActivity extends AppCompatActivity {

    private Button _startButton;
    private Button _registerButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        _startButton = findViewById((R.id.startButton));
        _startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Can Add if else case to go to login or by-pass the login
                openLoginActivity();
            }
        });

        _registerButton = findViewById((R.id.main_activity_register_button));
        _registerButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Can Add if else case to go to login or by-pass the login
                openRegisterActivity();
            }
        });

    }

    public void openLoginActivity() {
        Intent intent = new Intent(this, LoginActivity.class);
        startActivity(intent);
    }

    public void openRegisterActivity() {
        Intent intent = new Intent(this, SignUp.class);
        startActivity(intent);
    }
}
