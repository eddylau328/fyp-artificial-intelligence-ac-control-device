package com.example.fyp_ac_monitor.activity;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import com.example.fyp_ac_monitor.MyFirebase;
import com.example.fyp_ac_monitor.R;
import com.example.fyp_ac_monitor.utils.PreferenceUtils;

public class MainActivity extends AppCompatActivity {

    private Button _startButton;
    private Button _registerButton;

    private MyFirebase db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        db = new MyFirebase();

        _startButton = findViewById((R.id.startButton));
        _startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (PreferenceUtils.loadIsLogin(MainActivity.this) == true) {
                    String save_username = PreferenceUtils.loadUsername(MainActivity.this);
                    String save_password = PreferenceUtils.loadPassword(MainActivity.this);
                    validateUser(save_username, save_password);
                } else {
                    // Can Add if else case to go to login or by-pass the login
                    openLoginActivity();
                }
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
                                PreferenceUtils.saveUsername(input_username, MainActivity.this);
                                PreferenceUtils.savePassword(input_password, MainActivity.this);
                                PreferenceUtils.saveIsLogin(true, MainActivity.this);

                                openMenuActivity();

                            } else {
                                Toast.makeText(MainActivity.this, "Error!", Toast.LENGTH_SHORT).show();
                                PreferenceUtils.saveUsername("", MainActivity.this);
                                PreferenceUtils.savePassword("", MainActivity.this);
                                PreferenceUtils.saveIsLogin(false, MainActivity.this);

                                openLoginActivity();
                            }
                        }
                    });
                } else {
                    Toast.makeText(MainActivity.this, "Error!", Toast.LENGTH_SHORT).show();
                    Toast.makeText(MainActivity.this, "Error!", Toast.LENGTH_SHORT).show();
                    PreferenceUtils.saveUsername("", MainActivity.this);
                    PreferenceUtils.savePassword("", MainActivity.this);
                    PreferenceUtils.saveIsLogin(false, MainActivity.this);

                    openLoginActivity();
                }
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

    public void openMenuActivity() {
        Intent intent = new Intent(this, MenuActivity.class);
        startActivity(intent);
    }
}
