package com.example.fyp_ac_monitor;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

import com.google.firebase.firestore.FirebaseFirestore;

public class LoginActivity extends AppCompatActivity {

    private static final String TAG = "LoginActivity";

    private static final String KEY_USERNAME = "username";
    private static final String KEY_PASSWORD = "password";

    private FirebaseFirestore db = FirebaseFirestore.getInstance();

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

        _login.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                validate(_username.getText().toString(), _password.getText().toString());
            }
        });

    }

    private void validate(final String username, final String password){

    }


}
