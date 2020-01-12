package com.example.fyp_ac_monitor.utils;

import android.content.Context;
import android.content.SharedPreferences;

public class PreferenceUtils {

    public PreferenceUtils(){}

    public static void saveUsername(String username, Context context){
        SharedPreferences sharedPreferences = context.getSharedPreferences(Constants.SHARED_PREFS, Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPreferences.edit();

        editor.putString(Constants.KEY_USERNAME, username);
    }

    public static void savePassword(String password, Context context){
        SharedPreferences sharedPreferences = context.getSharedPreferences(Constants.SHARED_PREFS, Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPreferences.edit();

        editor.putString(Constants.KEY_PASSWORD, password);
    }

    public static void saveIsLogin(Boolean islogin, Context context){
        SharedPreferences sharedPreferences = context.getSharedPreferences(Constants.SHARED_PREFS, Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPreferences.edit();

        editor.putBoolean(Constants.KEY_ISLOGIN, islogin);
    }

    public static String loadUsername(Context context){
        SharedPreferences sharedPreferences = context.getSharedPreferences(Constants.SHARED_PREFS, Context.MODE_PRIVATE);
        return sharedPreferences.getString(Constants.KEY_USERNAME, "");
    }

    public static String loadPassword(Context context){
        SharedPreferences sharedPreferences = context.getSharedPreferences(Constants.SHARED_PREFS, Context.MODE_PRIVATE);
        return sharedPreferences.getString(Constants.KEY_PASSWORD, "");
    }

    public static boolean loadIsLogin(Context context){
        SharedPreferences sharedPreferences = context.getSharedPreferences(Constants.SHARED_PREFS, Context.MODE_PRIVATE);
        return sharedPreferences.getBoolean(Constants.KEY_ISLOGIN, false);
    }

}
