package com.example.fyp_ac_monitor.activity;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.example.fyp_ac_monitor.R;
import com.example.fyp_ac_monitor.utils.PreferenceUtils;
import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;

public class LoginActivity extends AppCompatActivity {

    private static final String TAG = "LoginActivity";

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

        _login.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Can Add if else case to go to login or by-pass the login
                validate();
            }
        });

    }

    public void validate(){
        final String input_username = _username.getText().toString();
        final String input_password = _password.getText().toString();

        if ("".equals(input_username) || "".equals(input_password)) {

            if ("".equals(input_username) && "".equals(input_password)){
                Toast.makeText(LoginActivity.this, "Empty username & password!", Toast.LENGTH_SHORT).show();
            } else if ("".equals(input_username)){
                Toast.makeText(LoginActivity.this, "Empty username!", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(LoginActivity.this, "Empty password!", Toast.LENGTH_SHORT).show();
            }
            return;
        }
        // this use to check the firestore where there is a username like the input
        checkUserExist(input_username, new MyCallBack() {
            @Override
            public void onCallback_isUserExist(boolean isUserExist) {
                if (isUserExist) {
                    DocumentReference userRef = db.collection("Users").document(input_username).collection("info").document("personal");
                    userRef.get()
                            .addOnSuccessListener(new OnSuccessListener<DocumentSnapshot>() {
                                @Override
                                public void onSuccess(DocumentSnapshot documentSnapshot) {
                                    // first check whether the user exists
                                    if (documentSnapshot.exists()) {
                                        // Toast.makeText(LoginActivity.this, "Username exists!", Toast.LENGTH_SHORT).show();
                                        // Second check whether the password is correct or not
                                        String password = documentSnapshot.getString(KEY_PASSWORD);
                                        if (input_password.equals(password)) {
                                            Toast.makeText(LoginActivity.this, "Login success", Toast.LENGTH_SHORT).show();
                                            openMenuActivity();
                                        } else {
                                            Toast.makeText(LoginActivity.this, "Wrong password!", Toast.LENGTH_SHORT).show();
                                        }
                                    } else {
                                        Toast.makeText(LoginActivity.this, "Error!", Toast.LENGTH_SHORT).show();
                                    }
                                }
                            })
                            .addOnFailureListener(new OnFailureListener() {
                                @Override
                                public void onFailure(@NonNull Exception e) {
                                    Toast.makeText(LoginActivity.this, "Error!", Toast.LENGTH_SHORT).show();
                                    Log.d(TAG, e.toString());
                                }
                            });
                } else {
                    Toast.makeText(LoginActivity.this, "Wrong username!", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    public void checkUserExist(String username, final MyCallBack myCallBack){
        // Access the user's username
        DocumentReference userRef = db.collection("Users").document(username).collection("info").document("personal");
        userRef.get()
                .addOnSuccessListener(new OnSuccessListener<DocumentSnapshot>() {
                    @Override
                    public void onSuccess(DocumentSnapshot documentSnapshot) {
                        // first check whether the user exists
                        if (documentSnapshot.exists()){
                            myCallBack.onCallback_isUserExist(true);
                        } else {
                            myCallBack.onCallback_isUserExist(false);
                        }
                    }
                })
                .addOnFailureListener(new OnFailureListener() {
                    @Override
                    public void onFailure(@NonNull Exception e) {
                        Toast.makeText(LoginActivity.this, "Error!", Toast.LENGTH_SHORT).show();
                        myCallBack.onCallback_isUserExist(true);
                        Log.d(TAG, e.toString());
                    }
                });
    }

    public interface MyCallBack {
        void onCallback_isUserExist(boolean isUserExist);
    }

    public void openMenuActivity() {
        Intent intent = new Intent(this, MenuActivity.class);
        startActivity(intent);
    }

}
