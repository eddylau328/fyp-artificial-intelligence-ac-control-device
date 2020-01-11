package com.example.fyp_ac_monitor;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.HashMap;
import java.util.Map;

public class SignUp extends AppCompatActivity {

    private static final String TAG = "SignupActivity";

    private static final String KEY_USERNAME = "username";
    private static final String KEY_PASSWORD = "password";
    private static final String KEY_EMAIL = "email";

    private FirebaseFirestore db = FirebaseFirestore.getInstance();

    private EditText _usernameInput;
    private EditText _passwordInput;
    private EditText _emailInput;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sign_up);

        _usernameInput = findViewById(R.id.register_username_input);
        _passwordInput = findViewById(R.id.register_password_input);
        _emailInput = findViewById(R.id.register_email_input);

    }

    public void saveUser(View v){
        String username = _usernameInput.getText().toString();
        String password = _passwordInput.getText().toString();
        String email = _emailInput.getText().toString();

        Map<String, Object> user = new HashMap<>();
        user.put(KEY_USERNAME, username);
        user.put(KEY_PASSWORD, password);
        user.put(KEY_EMAIL, email);

        db.collection("Users").document(username).set(user)
                .addOnSuccessListener(new OnSuccessListener<Void>() {
                    @Override
                    public void onSuccess(Void aVoid) {
                        Toast.makeText(SignUp.this, "User created!", Toast.LENGTH_SHORT).show();
                    }
                })
                .addOnFailureListener(new OnFailureListener() {
                    @Override
                    public void onFailure(@NonNull Exception e) {
                        Toast.makeText(SignUp.this, "Error!", Toast.LENGTH_SHORT).show();
                        Log.d(TAG, e.toString());
                    }
                });

    }
}
