package com.example.fyp_ac_monitor;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;

public class LoginActivity extends AppCompatActivity {

    private EditText _username;
    private EditText _password;
    private Button _login;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        _username = (EditText)findViewById(R.id.username_input);
        _password = (EditText)findViewById(R.id.password_input);
        _login = (Button)findViewById(R.id.login_button);

    }

    private void validate(String username, String password){

    }


}
