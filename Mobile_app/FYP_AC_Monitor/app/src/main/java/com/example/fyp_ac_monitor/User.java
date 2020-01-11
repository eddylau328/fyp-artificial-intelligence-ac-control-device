package com.example.fyp_ac_monitor;

public class User {
    String _email;
    String _username;
    String _password;

    public User(String _username, String _email, String _password){
        this._username = _username;
        this._password = _password;
        this._email = _email;
    }

    public String get_email() {
        return _email;
    }

    public void set_email(String _email) {
        this._email = _email;
    }

    public String get_username() {
        return _username;
    }

    public void set_username(String _username) {
        this._username = _username;
    }

    public String get_password() {
        return _password;
    }

    public void set_password(String _password) {
        this._password = _password;
    }
}
