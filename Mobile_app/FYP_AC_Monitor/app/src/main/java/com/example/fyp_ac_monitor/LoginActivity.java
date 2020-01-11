package com.example.fyp_ac_monitor;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

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

    }

    public void validate(View v){
        String input_username = _username.getText().toString();
        final String input_password = _password.getText().toString();

        // this use to check the firestore where there is a username like the input
        DocumentReference userRef = db.collection("Users").document(input_username);
        userRef.get()
                .addOnSuccessListener(new OnSuccessListener<DocumentSnapshot>() {
                    @Override
                    public void onSuccess(DocumentSnapshot documentSnapshot) {
                        // first check whether the user exists
                        if (documentSnapshot.exists()){
                            // Toast.makeText(LoginActivity.this, "Username exists!", Toast.LENGTH_SHORT).show();
                            // Second check whether the password is correct or not
                            String password = documentSnapshot.getString(KEY_PASSWORD);

                            if (input_password.equals(password)){
                                Toast.makeText(LoginActivity.this, "Login success", Toast.LENGTH_SHORT).show();
                            } else {
                                Toast.makeText(LoginActivity.this, "Wrong password!", Toast.LENGTH_SHORT).show();
                            }

                        } else {
                            Toast.makeText(LoginActivity.this, "Wrong username!", Toast.LENGTH_SHORT).show();
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
    }

}
