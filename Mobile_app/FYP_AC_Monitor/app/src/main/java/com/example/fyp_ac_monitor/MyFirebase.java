package com.example.fyp_ac_monitor;

import android.content.Context;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;

import com.example.fyp_ac_monitor.activity.LoginActivity;
import com.example.fyp_ac_monitor.utils.PreferenceUtils;
import com.google.android.gms.tasks.OnFailureListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.firestore.DocumentReference;
import com.google.firebase.firestore.DocumentSnapshot;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.FirebaseFirestoreSettings;
import com.google.firebase.firestore.Source;

public class MyFirebase {

    private static final String KEY_USERNAME = "username";
    private static final String KEY_PASSWORD = "password";
    private static final String KEY_EMAIL = "email";
    private static final String KEY_SERIAL_NUM = "id";

    private String TAG = "Firebase";

    private FirebaseFirestore db;
    private FirebaseDatabase rt_db;

    public MyFirebase (){
        db = FirebaseFirestore.getInstance();
        FirebaseFirestoreSettings settings = new FirebaseFirestoreSettings.Builder()
                .setPersistenceEnabled(false)
                .build();
        db.setFirestoreSettings(settings);
        rt_db = FirebaseDatabase.getInstance();

    }

    public void checkUserExist(final String username, final username_callback username_callback){
        // Access the user's username
        DocumentReference userRef = db.collection("Users").document(username).collection("info").document("personal");
        userRef.get(Source.SERVER)
                .addOnSuccessListener(new OnSuccessListener<DocumentSnapshot>() {
                    @Override
                    public void onSuccess(DocumentSnapshot documentSnapshot) {

                        // first check whether the user exists
                        if (documentSnapshot.exists()){
                            username_callback.onCallback_isUserExist(true);
                        } else {
                            username_callback.onCallback_isUserExist(false);
                        }
                    }
                })
                .addOnFailureListener(new OnFailureListener() {
                    @Override
                    public void onFailure(@NonNull Exception e) {
                        username_callback.onCallback_isUserExist(false);
                        Log.d(TAG, e.toString());
                    }
                });
    }

    public void checkPasswordCorrect(final String input_username, final String input_password,final password_callback password_callback){
        DocumentReference userRef = db.collection("Users").document(input_username).collection("info").document("personal");
        userRef.get(Source.SERVER)
                .addOnSuccessListener(new OnSuccessListener<DocumentSnapshot>() {
                    @Override
                    public void onSuccess(DocumentSnapshot documentSnapshot) {
                        // first check whether the user exists
                        if (documentSnapshot.exists()) {
                            // Toast.makeText(LoginActivity.this, "Username exists!", Toast.LENGTH_SHORT).show();
                            // Second check whether the password is correct or not
                            String password = documentSnapshot.getString(KEY_PASSWORD);
                            if (input_password.equals(password)) {
                                password_callback.onCallback_isPasswordCorrect(true);
                            } else {
                                password_callback.onCallback_isPasswordCorrect(false);
                            }
                        } else {
                            password_callback.onCallback_isPasswordCorrect(false);
                        }
                    }
                })
                .addOnFailureListener(new OnFailureListener() {
                    @Override
                    public void onFailure(@NonNull Exception e) {
                        password_callback.onCallback_isPasswordCorrect(false);
                        Log.d(TAG, e.toString());
                    }
                });
    }

    public interface username_callback {
        void onCallback_isUserExist(boolean isUserExist);
    }

    public interface password_callback {
        void onCallback_isPasswordCorrect(boolean isPasswordCorrect);
    }


    private void getUserConnectDeviceSerialNum(final String username, final String device_name, final serial_num_callback serial_num_callback){
        DocumentReference serial_numRef = db.collection("Users").document(username)
                .collection("connect_device").document(device_name);
        serial_numRef.get(Source.SERVER)
                .addOnSuccessListener(new OnSuccessListener<DocumentSnapshot>() {
                    @Override
                    public void onSuccess(DocumentSnapshot documentSnapshot) {
                        if (documentSnapshot.exists()){
                            String serial_num = documentSnapshot.getString(KEY_SERIAL_NUM);
                            serial_num_callback.onCallback_getSerialNum(true, serial_num);
                        }else{
                            serial_num_callback.onCallback_getSerialNum(false, "");
                        }
                    }
                })
                .addOnFailureListener(new OnFailureListener() {
                    @Override
                    public void onFailure(@NonNull Exception e) {
                        serial_num_callback.onCallback_getSerialNum(false, "");
                        Log.d(TAG, e.toString());
                    }
                });
    }

    public interface  serial_num_callback {
        void onCallback_getSerialNum(boolean getSerial, String serial_num);
    }


    public void sendControlCommand(final String username, final String send_command) {
        getUserConnectDeviceSerialNum(username, "ACmonitor", new serial_num_callback() {
            @Override
            public void onCallback_getSerialNum(boolean getSerial, String serial_num) {
                if (getSerial){
                    DatabaseReference commandRef = rt_db.getReference();
                    commandRef.child("Devices").child(serial_num).child("receive_action").child("command").setValue(send_command);
                    DatabaseReference is_new_actionRef = rt_db.getReference();
                    is_new_actionRef.child("Devices").child(serial_num).child("receive_action").child("is_new_action").setValue(true);
                }
            }
        });
    }

}
