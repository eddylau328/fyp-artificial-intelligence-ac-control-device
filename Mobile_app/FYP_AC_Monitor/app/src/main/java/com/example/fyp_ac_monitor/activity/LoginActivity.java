package com.example.fyp_ac_monitor.activity;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.example.fyp_ac_monitor.MyFirebase;
import com.example.fyp_ac_monitor.R;
import com.example.fyp_ac_monitor.utils.PreferenceUtils;


public class LoginActivity extends AppCompatActivity {

    private static final String TAG = "LoginActivity";

    private static final String KEY_PASSWORD = "password";

    private MyFirebase db;

    private EditText _username;
    private EditText _password;
    private Button _login;

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        _username = findViewById(R.id.username_input);
        _password = findViewById(R.id.password_input);
        _login = findViewById(R.id.login_button);

        _login.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Can Add if else case to go to login or by-pass the login
                final String input_username = _username.getText().toString();
                final String input_password = _password.getText().toString();
                validateUser(input_username, input_password);
            }
        });

        db = new MyFirebase();

    }


    public void validateUser(final String input_username, final String input_password){

        // this use to check the firestore where there is a username like the input
        db.checkUserExist(input_username, new MyFirebase.username_callback(){
            @Override
            public void onCallback_isUserExist( boolean isUserExist){
                if (isUserExist) {
                    db.checkPasswordCorrect(input_username, input_password, new MyFirebase.password_callback() {
                        @Override
                        public void onCallback_isPasswordCorrect ( boolean isPasswordCorrect){
                            if (isPasswordCorrect) {
                                Toast.makeText(LoginActivity.this, "Login success", Toast.LENGTH_SHORT).show();

                                PreferenceUtils.saveUsername(input_username, LoginActivity.this);
                                PreferenceUtils.savePassword(input_password, LoginActivity.this);
                                PreferenceUtils.saveIsLogin(true, LoginActivity.this);

                                openMenuActivity();

                            } else {
                                Toast.makeText(LoginActivity.this, "Wrong password!", Toast.LENGTH_SHORT).show();
                            }
                        }
                    });
                } else {
                    Toast.makeText(LoginActivity.this, "Wrong username!", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    public void openMenuActivity() {
        Intent intent = new Intent(this, MenuActivity.class);
        startActivity(intent);
    }

}
