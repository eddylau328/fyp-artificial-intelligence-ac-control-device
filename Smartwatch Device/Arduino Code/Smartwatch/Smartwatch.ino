#include <Wire.h>
#include "MAX30105.h"

#include <MPU6050_tockn.h>

#include "heartRate.h"

#include <SPI.h>
//#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <Timer.h>

#include <OneWire.h>
#include <DallasTemperature.h>

#include <WiFi.h>
#include <FirebaseESP32.h>

#define WIFI_SSID "Lau Family"
#define WIFI_PASSWORD "27050880"
#define FIREBASE_HOST "fypacmonitor.firebaseio.com"
#define FIREBASE_AUTH "jaT833r4mymesl03s37FD9jeV9JnWZzcM1xrnX8d"

//Define Firebase Data object
FirebaseData firebaseData;

void wifi_connect(){
  //connect to WiFi
  Serial.printf("Connecting to %s ", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println(" CONNECTED");
}

String serial_num = "watch0001";
String firebase_sensor_address = String("/Devices/"+serial_num+"/sensors");
String firebase_body_data_address = String("/Devices/"+serial_num+"/datapack");
String firebase_send_data_period = String("/Devices/fyp0001/receive_action/period");
String firebase_watch_move_type = String("/Devices/fyp0001/receive_action/move_type");
String firebase_start_send = String("/Devices/fyp0001/receive_action/is_send");
int SEND_PERIOD = 30;
String correct_move_type = "";
bool isSendData2Firebase = false;

void firebase_connect(){
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);
}

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define MIN_VOLTAGE_LEVEL 3.3
#define MAX_VOLTAGE_LEVEL 4.2
float battery_voltage;
int voltage_read_offset = 200;
Timer voltTimer;

void read_battery_voltage(){
  int sensor_value = analogRead(39) + 200;
  battery_voltage = (sensor_value*3.3/4095)*(30000+7500)/7500;
  Serial.println(battery_voltage);
}

enum Control{
  LEFT,RIGHT,ENTER,BACK
};

class Bitmap{
  public:
    int height;
    int width;
    unsigned char *pic;
    void set(unsigned char *pic, int width, int height){
      this->pic = pic;
      this->width = width;
      this->height = height;
    }
};


unsigned char pepe_pic_array [] PROGMEM = {
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x03, 0x83, 0x81, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x06, 0x00, 0xc6, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x08, 0x00, 0x38, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x10, 0x00, 0x10, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x20, 0x3f, 0x88, 0x00, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x40, 0xe0, 0xe8, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x43, 0x00, 0x1f, 0xff, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x80, 0x00, 0x04, 0x00, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x80, 0x07, 0xf6, 0x1f, 0xcc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x01, 0x00, 0x1f, 0xff, 0xef, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x03, 0x00, 0x33, 0xfd, 0x99, 0xfb, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x0f, 0x01, 0xff, 0x0f, 0xa7, 0xdf, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x19, 0x01, 0xf8, 0x01, 0x9c, 0x03, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x12, 0x06, 0x60, 0x00, 0x70, 0x40, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x32, 0x07, 0xc1, 0xf0, 0x41, 0xf0, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x20, 0x00, 0xc3, 0xd8, 0x43, 0xd8, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x60, 0x00, 0x33, 0xd9, 0xc3, 0xff, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x40, 0x00, 0x5f, 0xfe, 0xff, 0xfb, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0xc0, 0x00, 0x3f, 0xf7, 0x80, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x80, 0x00, 0x0f, 0xee, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x80, 0x00, 0x00, 0x08, 0x20, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x01, 0x00, 0x00, 0x00, 0x30, 0x1f, 0xf0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x01, 0x00, 0x00, 0x01, 0xc0, 0x06, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x02, 0x00, 0x01, 0xfe, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x02, 0x00, 0x03, 0x03, 0xc0, 0x00, 0x0f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x02, 0x00, 0x04, 0x00, 0x3f, 0xc3, 0xf9, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x02, 0x00, 0x04, 0x7e, 0x00, 0x7e, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x02, 0x00, 0x04, 0x01, 0xfc, 0x00, 0x1c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x03, 0x00, 0x16, 0x00, 0x07, 0xff, 0xec, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x01, 0x00, 0x13, 0xff, 0x80, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x80, 0x0c, 0x00, 0xff, 0xc0, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x60, 0x06, 0x00, 0x00, 0xff, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x01, 0xf0, 0x00, 0x00, 0x00, 0x01, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x03, 0x6e, 0x00, 0x00, 0x00, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x06, 0x31, 0xe0, 0x00, 0x00, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x0c, 0x0c, 0x3f, 0x80, 0x00, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x18, 0x03, 0x80, 0x7f, 0xff, 0xe0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x10, 0x00, 0x7e, 0x00, 0x07, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x20, 0x00, 0x01, 0xff, 0xfc, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x60, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x7f, 0xff, 0xff, 0xff, 0xff, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

unsigned char slogan_pic_array [] PROGMEM = {
0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0c,
0x00, 0x00, 0xe1, 0x80, 0x00, 0x00, 0x03, 0xe0, 0x10, 0x0e, 0x38, 0x00, 0x00, 0x08, 0x00, 0x00,
0x83, 0x00, 0x60, 0x01, 0xfe, 0x00, 0x0c, 0x0c, 0x30, 0x00, 0x00, 0x08, 0x0c, 0x01, 0x87, 0xff,
0xe0, 0x7c, 0x20, 0x00, 0x06, 0x0c, 0x30, 0x00, 0x08, 0x08, 0x18, 0x03, 0x04, 0x00, 0x00, 0x00,
0x20, 0x00, 0x02, 0x0c, 0x33, 0x00, 0x04, 0x08, 0x10, 0x02, 0x08, 0x00, 0x00, 0x00, 0x20, 0x1c,
0x00, 0x7f, 0xff, 0x00, 0x02, 0x08, 0x30, 0x04, 0x63, 0xff, 0xc1, 0xff, 0xff, 0xfc, 0x00, 0x0c,
0x30, 0x00, 0x03, 0x08, 0x20, 0x08, 0x42, 0x00, 0x80, 0x00, 0xe0, 0x00, 0x00, 0x0c, 0x30, 0x00,
0x01, 0x08, 0x40, 0x00, 0xc2, 0x00, 0x80, 0x01, 0xae, 0x00, 0x30, 0x0c, 0x30, 0x00, 0x01, 0x08,
0x80, 0x01, 0x83, 0xff, 0x80, 0x02, 0x23, 0xc0, 0x18, 0x0c, 0x31, 0x80, 0x00, 0x08, 0x02, 0x01,
0x02, 0x00, 0x80, 0x0c, 0x20, 0xf0, 0x0d, 0xff, 0xff, 0xc0, 0x7f, 0xff, 0xff, 0x03, 0x02, 0x00,
0x80, 0x18, 0x20, 0x38, 0x00, 0x08, 0x10, 0x00, 0x00, 0xc3, 0x00, 0x03, 0x83, 0xff, 0x80, 0x60,
0x20, 0x0c, 0x00, 0x18, 0x08, 0x00, 0x00, 0xc3, 0x00, 0x05, 0x02, 0x80, 0x81, 0x00, 0x20, 0x00,
0x00, 0x30, 0x1c, 0x00, 0x00, 0xc3, 0x00, 0x09, 0x00, 0xc0, 0x00, 0x1f, 0xff, 0xc0, 0x00, 0x3f,
0xff, 0x00, 0x00, 0x83, 0x00, 0x11, 0x00, 0x81, 0x80, 0x18, 0x00, 0xc0, 0x04, 0x58, 0x13, 0xc0,
0x00, 0x83, 0x00, 0x01, 0x03, 0xff, 0x80, 0x18, 0x00, 0xc0, 0x04, 0x98, 0x10, 0x00, 0x00, 0x83,
0x00, 0x01, 0x03, 0x01, 0x00, 0x18, 0x00, 0xc0, 0x0a, 0x18, 0x10, 0x00, 0x01, 0x83, 0x00, 0x01,
0x07, 0x83, 0x00, 0x1f, 0xff, 0xc0, 0x08, 0x1f, 0xf8, 0x00, 0x01, 0x03, 0x01, 0x01, 0x0c, 0xc6,
0x00, 0x18, 0x00, 0xc0, 0x10, 0x18, 0x00, 0x00, 0x03, 0x03, 0x01, 0x01, 0x10, 0x6c, 0x00, 0x18,
0x00, 0xc0, 0x30, 0x18, 0x01, 0x00, 0x06, 0x03, 0x01, 0x01, 0x00, 0x38, 0x00, 0x18, 0x00, 0xc0,
0x30, 0x18, 0x01, 0x00, 0x0c, 0x03, 0x01, 0x01, 0x00, 0x6e, 0x00, 0x18, 0x00, 0xc0, 0x60, 0x18,
0x01, 0x00, 0x10, 0x01, 0xff, 0x81, 0x01, 0x83, 0xe0, 0x1f, 0xff, 0xc0, 0x20, 0x0f, 0xff, 0x80,
0x40, 0x00, 0x28, 0x01, 0x1e, 0x00, 0xe0, 0x18, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01, 0xc0, 0x00, 0x70, 0x60, 0x00, 0x06,
0x06, 0x00, 0x00, 0x0e, 0x00, 0x00, 0x03, 0x01, 0x80, 0x00, 0x60, 0x66, 0x00, 0x04, 0x06, 0x18,
0x00, 0x0a, 0x00, 0x00, 0xff, 0x01, 0x86, 0x00, 0x40, 0x61, 0x01, 0xff, 0xff, 0xfc, 0x00, 0x11,
0x00, 0x00, 0xc3, 0x3f, 0xff, 0x00, 0xc0, 0x61, 0x80, 0x04, 0x06, 0x00, 0x00, 0x20, 0x80, 0x00,
0xc3, 0x01, 0x80, 0x00, 0x80, 0x60, 0x80, 0x04, 0x06, 0x00, 0x00, 0x40, 0x60, 0x00, 0xc3, 0x01,
0x80, 0x01, 0x80, 0x60, 0x00, 0x04, 0x06, 0x00, 0x01, 0x80, 0x18, 0x00, 0xc3, 0x01, 0x80, 0x01,
0x00, 0x60, 0x70, 0x07, 0xfe, 0x00, 0x02, 0x00, 0x6e, 0x00, 0xc3, 0x01, 0x88, 0x03, 0x80, 0x7f,
0x80, 0x04, 0x60, 0x00, 0x0c, 0xff, 0xe3, 0xc0, 0xc3, 0x1f, 0xfe, 0x03, 0x3f, 0xe0, 0x00, 0x00,
0x60, 0x00, 0x30, 0x00, 0x00, 0x00, 0xc3, 0x00, 0x00, 0x05, 0x00, 0x20, 0x00, 0x20, 0x60, 0x40,
0x00, 0x00, 0x00, 0x00, 0xff, 0x00, 0x18, 0x09, 0x00, 0x20, 0x00, 0x7f, 0xff, 0xe0, 0x18, 0x23,
0x03, 0x00, 0xc3, 0x00, 0x10, 0x09, 0x00, 0x20, 0x00, 0x60, 0x60, 0x60, 0x1f, 0xf3, 0xff, 0x00,
0xc3, 0x00, 0x13, 0x11, 0x00, 0x20, 0x00, 0x60, 0x60, 0x60, 0x18, 0x23, 0x02, 0x00, 0xc3, 0x7f,
0xff, 0x81, 0x00, 0x30, 0x00, 0x60, 0x60, 0x60, 0x18, 0x23, 0x02, 0x00, 0xc3, 0x00, 0x10, 0x01,
0x00, 0x10, 0x00, 0x7f, 0xff, 0xe0, 0x18, 0x23, 0x02, 0x00, 0xc3, 0x00, 0x10, 0x01, 0x00, 0x10,
0x00, 0x60, 0x60, 0x00, 0x18, 0x23, 0x02, 0x00, 0xc3, 0x18, 0x10, 0x01, 0x00, 0x18, 0x00, 0x00,
0x60, 0x00, 0x18, 0x23, 0x02, 0x00, 0xc3, 0x0c, 0x10, 0x01, 0x00, 0x08, 0x10, 0x00, 0x60, 0x0c,
0x18, 0x23, 0x02, 0x00, 0xff, 0x06, 0x10, 0x01, 0x00, 0x0c, 0x13, 0xff, 0xff, 0xfe, 0x1f, 0xf3,
0x02, 0x00, 0xc3, 0x04, 0x10, 0x01, 0x00, 0x04, 0x10, 0x00, 0x60, 0x00, 0x18, 0x03, 0x3e, 0x00,
0x00, 0x00, 0x10, 0x01, 0x00, 0x02, 0x20, 0x00, 0x60, 0x00, 0x00, 0x03, 0x06, 0x00, 0x00, 0x00,
0x10, 0x01, 0x00, 0x01, 0xa0, 0x00, 0x60, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x01, 0xf0, 0x01,
0x00, 0x00, 0xe0, 0x00, 0x60, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x70, 0x01, 0x80, 0x00,
0x70, 0x00, 0x60, 0x00, 0x00, 0x03, 0x00, 0x00
};

unsigned char battery_pic_array [] PROGMEM =  {
 0xff, 0xff, 0xe0, 0x80, 0x00, 0x20, 0x80, 0x00, 0x30, 0x80, 0x00, 0x10, 0x80, 0x00, 0x10, 0x80,
  0x00, 0x10, 0x80, 0x00, 0x30, 0x80, 0x00, 0x20, 0xff, 0xff, 0xe0
};

Bitmap battery_pic;
Bitmap pepe_pic;
Bitmap slogan_pic;

void bitmap_initialize(){
  battery_pic.set(battery_pic_array,20, 9);
  pepe_pic.set(pepe_pic_array,128, 64);
  slogan_pic.set(slogan_pic_array, 106,60);
}


MAX30105 particleSensor;

const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred

float beatsPerMinute;
int beatAvg;

/********************************************************************/
// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 32
/********************************************************************/
// Setup a oneWire instance to communicate with any OneWire devices
// (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
/********************************************************************/
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature bodyTempSensor(&oneWire);
/********************************************************************/
float bodyTemp, avgBodyTemp;
int bodyTempCount = 0;

float acc[3] = {0,0,0};
float gyr[3] = {0,0,0};

class DataPack{
  public:
    float acc[3];

    void set_acc(float acc[]){
      for (int i = 0 ; i < 3 ; i ++)
        this->acc[i] = acc[i];
    }

    void set_json_data(FirebaseJson *json_data, String type){
      json_data->add("acc_x", acc[0]);
      json_data->add("acc_y", acc[1]);
      json_data->add("acc_z", acc[2]);
      json_data->add("move_type", type);
    }
};

Timer tempTimer;
Timer mpu6050Timer;

MPU6050 mpu6050(Wire);

// OneWire DS18S20, DS18B20, DS1822 Temperature Example
//
// http://www.pjrc.com/teensy/td_libs_OneWire.html
//
// The DallasTemperature library can do all this work for you!
// https://github.com/milesburton/Arduino-Temperature-Control-Library

OneWire  ds(32);  // on pin 10 (a 4.7K resistor is necessary)


void heartRateSensorSetup(){
  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup(); //Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); //Turn off Green
}

/*========================================================================================================
                                          OLED PART START
  ========================================================================================================*/

class OLED{
  public:
    Adafruit_SSD1306 *oled;

    OLED(Adafruit_SSD1306 *oled){
      this->oled = oled;
      // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
      if(!oled->begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x32
        Serial.println(F("SSD1306 allocation failed"));
        for(;;); // Don't proceed, loop forever
      }

      // Show initial display buffer contents on the screen --
      // the library initializes this with an Adafruit splash screen.
      oled->display();
      delay(2000); // Pause for 2 seconds
      clear();
    }

    void display_pic(unsigned char bmp [],int width, int height, bool light_up) {
      int color = light_up? SSD1306_WHITE : SSD1306_BLACK;
      oled->drawBitmap(
      (oled->width()  - width ) / 2,
      (oled->height() - height) / 2,
      bmp, width, height, color);
      oled->display();
    }

    void display_pic(unsigned char bmp [],int width, int height,int x, int y, bool light_up) {
      int color = light_up? SSD1306_WHITE : SSD1306_BLACK;
      oled->drawBitmap(x, y,bmp, width, height, color);
      oled->display();
    }

    void display_text(String text, int x, int y, bool light_up) {
      int color = light_up? SSD1306_WHITE : SSD1306_BLACK;
      oled->setTextSize(1);             // Normal 1:1 pixel scale
      oled->setTextColor(color);        // Draw white text
      oled->setCursor(x,y);             // Start at top-left corner
      oled->println(text);
      oled->display();
    }

    void display_text(String text, int x, int y, bool light_up, int text_size) {
      int color = light_up? SSD1306_WHITE : SSD1306_BLACK;
      oled->setTextSize(text_size);             // Normal 1:1 pixel scale
      oled->setTextColor(color);        // Draw white text
      oled->setCursor(x,y);             // Start at top-left corner
      oled->println(text);
      oled->display();
    }

    void display_text(float text, int decimal_place, int x, int y, bool light_up, int text_size) {
      int color = light_up? SSD1306_WHITE : SSD1306_BLACK;
      oled->setTextSize(text_size);             // Normal 1:1 pixel scale
      oled->setTextColor(color);        // Draw white text
      oled->setCursor(x,y);             // Start at top-left corner
      oled->println(text, decimal_place);
      oled->display();
    }

    void display_text(int text, int x, int y, bool light_up, int text_size) {
      int color = light_up? SSD1306_WHITE : SSD1306_BLACK;
      oled->setTextSize(text_size);             // Normal 1:1 pixel scale
      oled->setTextColor(color);        // Draw white text
      oled->setCursor(x,y);             // Start at top-left corner
      oled->println(text);
      oled->display();
    }

    void display_text(String text, int x, int y, bool light_up, int text_size, bool highlight) {
      int color;
      int bg_color;
      if (highlight == true && light_up == true){
        color = SSD1306_BLACK;
        bg_color = SSD1306_WHITE;
        oled->setTextSize(text_size);             // Normal 1:1 pixel scale
        oled->setTextColor(color, bg_color);        // Draw white text
        oled->setCursor(x,y);             // Start at top-left corner
        oled->println(text);
        oled->display();
      }else if (highlight == false && light_up == true){
        color = SSD1306_WHITE;
        bg_color = SSD1306_BLACK;
        oled->setTextSize(text_size);             // Normal 1:1 pixel scale
        oled->setTextColor(color, bg_color);        // Draw white text
        oled->setCursor(x,y);             // Start at top-left corner
        oled->println(text);
        oled->display();
      }else if (highlight == true && light_up == false){
        color = SSD1306_WHITE;
        bg_color = SSD1306_BLACK;
        oled->setTextSize(text_size);             // Normal 1:1 pixel scale
        oled->setTextColor(color, bg_color);
        oled->setCursor(x,y);             // Start at top-left corner
        oled->println(text);

        color = SSD1306_BLACK;
        oled->setTextSize(text_size);             // Normal 1:1 pixel scale
        oled->setTextColor(color, bg_color);
        oled->setCursor(x,y);             // Start at top-left corner
        oled->println(text);
        oled->display();
      }else{
        color = SSD1306_BLACK;
        bg_color = SSD1306_BLACK;
        oled->setTextSize(text_size);             // Normal 1:1 pixel scale
        oled->setTextColor(color, bg_color);        // Draw white text
        oled->setCursor(x,y);             // Start at top-left corner
        oled->println(text);
        oled->display();
      }
    }

    void display_pixel(int x, int y, bool light_up){
        int color = light_up? SSD1306_WHITE : SSD1306_BLACK;
        // Draw a single pixel in white
        oled->drawPixel(x, y, color);
        // Show the display buffer on the screen. You MUST call display() after
        // drawing commands to make them visible on screen!
        oled->display();
    }

    void display_rect(int x, int y, int w, int h, bool light_up){
      int color = light_up? SSD1306_WHITE : SSD1306_BLACK;
      //oled->drawRect(x,y,w,h,color);
      oled->fillRect(x,y,w,h,color);
      oled->display();
    }

    void clear(){
      oled->clearDisplay();
    }

};

/*========================================================================================================
                                          OLED PART END
  ========================================================================================================*/


/*========================================================================================================
                                          PAGE PART START
  ========================================================================================================*/

#define INITIAL_PAGE 0
#define MAIN_PAGE 1
#define TEMP_PAGE 2
#define MOVE_PAGE 3
#define MENU_PAGE 4
#define EMPTY_PAGE 5
#define TOTAL_PAGE 6

/* ------------------------------------------------------------------------

main_page -> temp_page -> move_page -> main_page
         Right       Right        Right

main_page <- temp_page <- move_page <- main_page
         Left         Left         Left

main_page -> menu_page  |  main_page <- menu_page
         Enter          |            Back

--------------------------------------------------------------------------- */
// page is the same base object of different page that the oled will display
class Page{
  public:
    bool isReverse = false;
    // methods that can be override
    virtual void show(OLED oled){}
    virtual void update(OLED oled){}
    virtual void active_update(OLED oled, Control motion){}
    virtual void clear(OLED oled){}
    bool get_isReverse(){return isReverse;}
};

class InitialPage: public Page{
  public:
    void show(OLED oled){
      for (int i = 0; i < 6; i++){
        oled.display_pixel(10+i*5, 32, true);
        delay(250);
      }

      for (int i = 0; i < 6; i++){
        oled.display_pixel(10+i*5, 32, false);
      }

      oled.display_text("Welcome back, Eddy!", 0, 32, true);
      delay(2000);
      oled.display_text("Welcome back, Eddy!", 0, 32, false);

      /*
      oled.display_pic(slogan_pic.pic,slogan_pic.width, slogan_pic.height,true);
      delay(3000);
      oled.display_pic(slogan_pic.pic,slogan_pic.width, slogan_pic.height,false);

      oled.display_pic(pepe_pic.pic,pepe_pic.width, pepe_pic.height,true);
      delay(3000);
      oled.display_pic(pepe_pic.pic,pepe_pic.width, pepe_pic.height,false);
      */
    }
};

class MainPage: public Page{
  private:
    // used to save the update
    float last_bodyTemp;
    float last_acc[3];
    float last_gyr[3];
    float* bodyTemp;
    float* acc, * gry;

  public:
    // override function
    void show(OLED oled){
      //oled.display_text("BMP:", 0, 22, true, 1);
      oled.display_text("TMP:", 0, 32, true, 1);
      //oled.display_text("Ang:", 0, 42, true, 1);
      oled.display_text("Acc:", 0, 52, true, 1);
    }
    // override function
    void clear(OLED oled){
      //oled.display_text("BMP:", 0, 22, false, 1);
      oled.display_text("TMP:", 0, 32, false, 1);
      //oled.display_text("Ang:", 0, 42, false, 1);
      oled.display_text("Acc:", 0, 52, false, 1);

      // clear update part
      oled.display_text(last_bodyTemp, 2,30, 32, false,1);
      for (int i = 0; i < 3; i++){
        //oled.display_text(last_gyr[i], 0,30+i*35, 42, false, 1);
        oled.display_text(last_acc[i], 1,30+i*35, 52, false, 1);
      }

      // reset update_part
      last_bodyTemp = 0;
      for (int i = 0; i < 3; i++){
        last_acc[i] = 0;
        //last_gyr[i] = 0;
      }
    }

    // override function
    void update(OLED oled){

      /*
      if (lastStrBeatAvg != strBeatAvg){
        oledClearText(lastStrBeatAvg,30, 22, 1);
        oledDisplayText(strBeatAvg, 30, 22, false, 1);
      }
      lastStrBeatAvg = strBeatAvg;
      */

      if (last_bodyTemp != *bodyTemp){
        oled.display_text(last_bodyTemp,2,30, 32, false,1);
        oled.display_text(*bodyTemp,2, 30, 32, true, 1);
      }
      last_bodyTemp = *bodyTemp;
      /*
      for (int i = 0; i < 3; i++){
        if (last_gyr[i] != gry[i]){
          oled.display_text(last_gyr[i],0, 30+i*35, 42, false, 1);
          oled.display_text(gyr[i],0, 30+i*35, 42, true, 1);
        }
      }
      for (int i=0; i<3; i++){
        last_gyr[i] = gyr[i];
      }
      */
      for (int i=0; i<3; i++){
        if (last_acc[i] != acc[i]){
          oled.display_text(last_acc[i], 1,30+i*35, 52, false, 1);
          oled.display_text(acc[i], 1, 30+i*35, 52, true, 1);
        }
      }
      for (int i=0; i<3; i++){
        last_acc[i] = acc[i];
      }
    }

    // connect the object data, which means saving the address and point to the same value
    void set_parameters(float* bodyTemp, float* acc, float* gry){
      this->bodyTemp = bodyTemp;  // linking to the global variable
      this->acc = acc;            // linking to the global variable
      //this->gry = gry;            // linking to the global variable
    }
};

class MenuPage: public Page{
  private:
    int pos[2][2] = {{1 , 0}, {0 , 0}};
    String strlist[2][2] = {{"Wifi:","ON"}, {"Send:", "ON"}};
    //String str_status_list[2];
    //bool *wifi_status, *send_status;

  public:
    // override function
    void show(OLED oled){
      for (int i = 0 ; i < 2; i++){
        for (int j = 0 ; j < 2; j++){
          oled.display_text(strlist[i][j], 0 + j*32, 22 + i*10, true, 1, pos[i][j]);
        }
      }
    }
    // override function
    void clear(OLED oled){
      for (int i = 0 ; i < 2; i++){
        for (int j = 0 ; j < 2; j++){
          oled.display_text(strlist[i][j], 0 + j*32, 22 + i*10, false, 1, pos[i][j]);
          pos[i][j] = 0;
        }
      }
      pos[0][0] = 1;
      isReverse = false;
    }

    void active_update(OLED oled, Control control){
      bool isPass = false;
      switch(control){
        case LEFT:
          Serial.println("pass left");
          for (int j = 0; j < 2 ; j++){
            for (int i = 0; i < 2 ; i++){
              if(pos[i][j] == 1){
                if (i-1 < 0){
                  pos[(i-1+2)%2][j] = 1;
                }else{
                  pos[(i-1)%2][j] = 1;
                }
                pos[i][j] = 0;
                isPass = true;
                break;
              }
            }
            if (isPass == true){
              break;
            }
          }
          break;
        case RIGHT:
          Serial.println("pass right");
          for (int j = 0; j < 2 ; j++){
            for (int i = 0; i < 2 ; i++){
              if(pos[i][j] == 1){
                pos[(i+1)%2][j] = 1;
                pos[i][j] = 0;
                isPass = true;
                break;
              }
            }
            if (isPass == true)
              break;
           }
           break;
        case ENTER:
          Serial.println("pass enter");
          for (int j = 0; j < 2 ; j++){
            for (int i = 0; i < 2 ; i++){
              if(pos[i][j] == 1 && j < 1){
                pos[i][j] = 0;
                pos[i][j+1] = 1;
                isPass = true;
                break;
              }
            }
            if (isPass == true)
              break;
          }
          break;
        case BACK:
          Serial.println("pass back");
          for (int j = 0; j < 2 ; j++){
            for (int i = 0; i < 2 ; i++){
              if(pos[i][j] == 1){
                if (j>0){
                  pos[i][j-1] = 1;
                  pos[i][j] = 0;
                  isPass = true;
                  break;
                }else{
                  isReverse = true;
                  isPass = true;
                  break;
                }
              }
            }
            if (isPass == true)
              break;
          }
          break;
      }
      if(!isReverse){
        for (int j = 0; j < 2 ; j++){
          for (int i = 0; i < 2 ; i++){
            oled.display_text(strlist[i][j], 0 + j*32, 22 + i*10, true, 1, pos[i][j]);
          }
        }
      }
    }
};

class TempPage: public Page{
  private:
    float last_bodyTemp;
    float* bodyTemp;
  public:
    // override function
    void show(OLED oled){
      oled.display_text("Temperature: ", 0, 22, true, 1);
    }
    // override function
    void clear(OLED oled){
      oled.display_text("Temperature: ", 0, 22, false, 1);

      // clear update part
      oled.display_text(last_bodyTemp,2,30, 32, false,1);

      // reset update_part
      last_bodyTemp = 0;

    }
    // override function
    void update(OLED oled){
      if (last_bodyTemp != *bodyTemp){
        oled.display_text(last_bodyTemp,2,30, 32, false,1);
        oled.display_text(*bodyTemp,2, 30, 32, true, 1);
      }
      last_bodyTemp = *bodyTemp;
    }
    // connect the object data, which means saving the address and point to the same value
    void set_parameters(float* bodyTemp){
      this->bodyTemp = bodyTemp;  // linking to the global variable
    }
};

class EmptyPage: public Page{
  public:
    void show(OLED oled){
      oled.clear();      
    }
    // override function
    void clear(OLED oled){}
    // override function
    void update(OLED oled){}
};

class MovePage: public Page{
  private:
    // used to save the update
    float last_acc[3];
    float last_gyr[3];
    float* acc, * gry;
  public:
    // override function
    void show(OLED oled){
      oled.display_text("Acceleration: ", 0, 22, true, 1);
      //oled.display_text("Euler Angle: ", 0, 42, true, 1);
    }
    // override function
    void clear(OLED oled){
      oled.display_text("Acceleration: ", 0, 22, false, 1);
      //oled.display_text("Euler Angle: ", 0, 42, false, 1);

      // clear update_part
      for (int i = 0; i < 3; i++){
        oled.display_text(last_acc[i], 1,10+i*35, 32, false, 1);
        //oled.display_text(last_gyr[i],0, 10+i*35, 52, false, 1);
      }

      // reset update_part
      for (int i = 0; i < 3; i++){
        last_acc[i] = 0;
        //last_gyr[i] = 0;
      }
    }
    // override function
    void update(OLED oled){
      for (int i=0; i<3; i++){
        if (last_acc[i] != acc[i]){
          oled.display_text(last_acc[i], 1,10+i*35, 32, false, 1);
          oled.display_text(acc[i], 1, 10+i*35, 32, true, 1);
        }
      }
      for (int i=0; i<3; i++){
        last_acc[i] = acc[i];
      }
      /*
      for (int i = 0; i < 3; i++){
        if (last_gyr[i] != gry[i]){
          oled.display_text(last_gyr[i],0, 10+i*35, 52, false, 1);
          oled.display_text(gyr[i],0, 10+i*35, 52, true, 1);
        }
      }
      for (int i=0; i<3; i++){
        last_gyr[i] = gyr[i];
      }
      */
    }
    // connect the object data, which means saving the address and point to the same value
    void set_parameters(float* acc, float* gry){
      this->acc = acc;            // linking to the global variable
      //this->gry = gry;            // linking to the global variable
    }
};

class NavBar{
  private:
    int last_battery_volt_level;
    float* battery_volt_level;
    
  public:
    // override function
    void show(OLED oled){
      oled.display_text("FYP", 0, 0, true, 2);
      oled.display_pic(battery_pic.pic,battery_pic.width, battery_pic.height, 105, 0, true);
      batterylevel_display(oled, true);
    }
    // override function
    void clear(OLED oled){
      oled.display_text("FYP", 0, 0, false, 2);
      oled.display_pic(battery_pic.pic,battery_pic.width, battery_pic.height, 105, 0, false);

      batterylevel_display(oled, false);
    }
    
    void set_parameters(float *battery_volt_level){
      this->battery_volt_level = battery_volt_level;
    }

    void update(OLED oled){
      int battery_level = (*battery_volt_level - MIN_VOLTAGE_LEVEL)/(MAX_VOLTAGE_LEVEL-MIN_VOLTAGE_LEVEL) * 15;
      if (last_battery_volt_level != battery_level){
        last_battery_volt_level = battery_level;
        batterylevel_display(oled, false);
        batterylevel_display(oled, true);
      }
    }

    void batterylevel_display(OLED oled, bool lightup){
       oled.display_rect(107,2,last_battery_volt_level,5,lightup);
    }
};

class PageMonitor{
  private:
    Page *pages[TOTAL_PAGE];
    NavBar *nav_bar;
    int current_page = -1;
    int last_page = -1;
    OLED *oled;

  public:
    void set(OLED *oled, Page *pages[], NavBar *nav_bar){
      this->oled = oled;
      this->nav_bar = nav_bar;
      for (int i = 0 ; i < TOTAL_PAGE; i++){
        this-> pages[i] = pages[i];
      }
    }

    void show(int page_num){
      if (current_page != -1){
        pages[current_page]->clear(*oled);
        if (current_page == EMPTY_PAGE){
          show_nav_bar();
          last_page = MENU_PAGE;
        }else
          last_page = current_page;
      }
      pages[page_num]->show(*oled);
      if (page_num == EMPTY_PAGE)
        nav_bar->clear(*oled);        
      Serial.println(page_num);
      current_page = page_num;
    }

    void update(){
      pages[current_page]->update(*oled);
      if (current_page != EMPTY_PAGE)
        nav_bar->update(*oled);
    }

    void active_update(Control control){
        pages[current_page]->active_update(*oled, control);
        if (pages[current_page]->get_isReverse()){
          pages[current_page]->clear(*oled);
          pages[last_page]->show(*oled);
          current_page = last_page;
          last_page = -1;
        }
    }

    void show_nav_bar(){
      nav_bar->show(*oled);
    }

    int get_current_page(){
      return current_page;
    }
};
/*========================================================================================================
                                          PAGE PART END
  ========================================================================================================*/


/*========================================================================================================
                                          BUTTON PART START
  ========================================================================================================*/
#define ENTER_BUTTON 0
#define ENTER_BUTTON_PIN 35
#define BACK_BUTTON 1
#define BACK_BUTTON_PIN 36
#define LEFT_BUTTON 2
#define LEFT_BUTTON_PIN 33
#define RIGHT_BUTTON 3
#define RIGHT_BUTTON_PIN 34

#define TOTAL_BUTTON 4

class Button{
  public:
    int pin_num;
    // override function that trigger when user push button
    virtual void call(PageMonitor *page_monitor){}

    void set(int pin_num){
      this->pin_num = pin_num;
      pinMode(pin_num, INPUT);
    }

    bool check_state(){
      // digitalRead function stores the Push button state
      // in variable push_button_state
      int Push_button_state = digitalRead(pin_num);
      // if condition checks if push button is pressed
      if ( Push_button_state == HIGH )
        return true;
      else
        return false;
    }
};

class EnterButton: public Button{
  public:
    // when enter button is called
    void call(PageMonitor *page_monitor){
      Serial.println("press enter button");
      int current_page = page_monitor->get_current_page();
      switch(current_page){
        // when the location is at MENU_PAGE
        case MAIN_PAGE:
          page_monitor->show(MENU_PAGE);
          break;
        case MENU_PAGE:
          // check cursor and click
          page_monitor->active_update(ENTER);
          break;
        case TEMP_PAGE:
          page_monitor->show(MENU_PAGE);
          break;
        case MOVE_PAGE:
          page_monitor->show(MENU_PAGE);
          break;
        case INITIAL_PAGE:
          // nothing needs to be happen
          break;
        case EMPTY_PAGE:
          page_monitor->show(MAIN_PAGE);
          break;
      }
    }
};

class BackButton: public Button{
  public:
    void call(PageMonitor *page_monitor){
      Serial.println("press back button");
      int current_page = page_monitor->get_current_page();
      switch(current_page){
        // when the location is at MENU_PAGE
        case MAIN_PAGE:
          //nothing needs to be happen
          break;
        case MENU_PAGE:
          page_monitor->active_update(BACK);
          break;
        case TEMP_PAGE:
          page_monitor->show(MAIN_PAGE);
          break;
        case MOVE_PAGE:
          page_monitor->show(MAIN_PAGE);
          break;
        case INITIAL_PAGE:
          //nothing needs to be happen
          break;
        case EMPTY_PAGE:
          page_monitor->show(MAIN_PAGE);
          break;
      }
    }
};

class LeftButton: public Button{
  public:
    void call(PageMonitor *page_monitor){
      Serial.println("press left button");
      int current_page = page_monitor->get_current_page();
      switch(current_page){
        // when the location is at MENU_PAGE
        case MAIN_PAGE:
          page_monitor->show(MOVE_PAGE);
          break;
        case MENU_PAGE:
          // move cursor (up)
          page_monitor->active_update(LEFT);
          break;
        case TEMP_PAGE:
          page_monitor->show(MAIN_PAGE);
          break;
        case MOVE_PAGE:
          page_monitor->show(TEMP_PAGE);
          break;
        case INITIAL_PAGE:
          //nothing needs to be happen
          break;
        case EMPTY_PAGE:
          page_monitor->show(MAIN_PAGE);
          break;
      }
    }
};

class RightButton: public Button{
  public:
    void call(PageMonitor *page_monitor){
      Serial.println("press right button");
      int current_page = page_monitor->get_current_page();
      switch(current_page){
        // when the location is at MENU_PAGE
        case MAIN_PAGE:
          page_monitor->show(TEMP_PAGE);
          break;
        case MENU_PAGE:
          //move cursor (down)
          page_monitor->active_update(RIGHT);
          break;
        case TEMP_PAGE:
          page_monitor->show(MOVE_PAGE);
          break;
        case MOVE_PAGE:
          page_monitor->show(MAIN_PAGE);
          break;
        case INITIAL_PAGE:
          //nothing needs to be happen
          break;
        case EMPTY_PAGE:
          page_monitor->show(MAIN_PAGE);
          break;
      }
    }
};

// Button Monitor is used to control different buttons
class ButtonMonitor{
  public:
    Button *buttons[TOTAL_BUTTON];
    int button_hold = -1;
    Timer timer;

    void set(Button *buttons[]){
      for (int i = 0; i < TOTAL_BUTTON; i++){
        this->buttons[i] = buttons[i];
      }
      timer.settimer(100);
      timer.starttimer();
    }

    // check whether any button is triggered
    bool check_trigger(PageMonitor *page_monitor){
      bool interact = false;
      if (timer.checkfinish()){
      bool any_button_on = false;
      for (int i = 0; i < TOTAL_BUTTON; i++){
        if (buttons[i]->check_state()){
          if (button_hold == -1){
            buttons[i]->call(page_monitor);
            button_hold = i;
          }
          any_button_on = true;
          interact = true;
          timer.resettimer();
          timer.starttimer();
        }
      }

      if (!any_button_on)
        button_hold = -1;
      }

      return interact;
    }

};

/*========================================================================================================
                                          BUTTON PART END
  ========================================================================================================*/


// Create PageMonitor and pages that is needed
PageMonitor page_monitor;
Page *pages[TOTAL_PAGE];
InitialPage initial_page;
MainPage main_page;
MenuPage menu_page;
TempPage temp_page;
MovePage move_page;
EmptyPage empty_page;
NavBar nav_bar;
// initialize the pages the smartwatch needed
void page_initialize(){
  bitmap_initialize();

  // PAGE SETUP --------------------------------
  // set up the parameters for update, which the page may need
  main_page.set_parameters(&bodyTemp, acc, gyr);
  temp_page.set_parameters(&bodyTemp);
  move_page.set_parameters(acc, gyr);
  nav_bar.set_parameters(&battery_voltage);
  pages[INITIAL_PAGE] = &initial_page;
  pages[MAIN_PAGE] = &main_page;
  pages[MENU_PAGE] = &menu_page;
  pages[MOVE_PAGE] = &move_page;
  pages[TEMP_PAGE] = &temp_page;
  pages[EMPTY_PAGE] = &empty_page;

  // create a page monitor
  page_monitor.set(new OLED(&display), pages, &nav_bar);
  // -------------------------------------------
}


// Create button and the function
ButtonMonitor button_monitor;
Button *buttons[TOTAL_BUTTON];
EnterButton enter_button;
BackButton back_button;
RightButton right_button;
LeftButton left_button;

void button_initialize(){
  // BUTTON SETUP ------------------------------
  enter_button.set(ENTER_BUTTON_PIN);
  buttons[ENTER_BUTTON] = &enter_button;

  back_button.set(BACK_BUTTON_PIN);
  buttons[BACK_BUTTON] = &back_button;

  right_button.set(RIGHT_BUTTON_PIN);
  buttons[RIGHT_BUTTON] = &right_button;

  left_button.set(LEFT_BUTTON_PIN);
  buttons[LEFT_BUTTON] = &left_button;

  button_monitor.set(buttons); // create a button monitor
  // -------------------------------------------
}

Timer interactTimer;

// ---------------------------------------------------------------------------
volatile int interruptCounter;
int totalInterruptCounter;
 
hw_timer_t * esp32_timer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;
 
void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);
  interruptCounter++;
  portEXIT_CRITICAL_ISR(&timerMux);
 
}

void esp32_timer_initialize(){
  esp32_timer = timerBegin(0, 80, true);
  timerAttachInterrupt(esp32_timer, &onTimer, true);
  timerAlarmWrite(esp32_timer, 1000000, true);
  timerAlarmEnable(esp32_timer);
}

// ---------------------------------------------------------------------------

DataPack datapack[4];
int pack_counter = 0;

void setup()
{
  Serial.begin(115200);
  Serial.println("Initializing...");

  page_initialize();
  button_initialize();

  page_monitor.show(INITIAL_PAGE);

  wifi_connect();
  firebase_connect();
  Firebase.getInt(firebaseData, firebase_send_data_period, SEND_PERIOD);
  Wire.begin();
  mpu6050.begin();

  //23:17:43.783 -> X : -1.35
  //23:17:43.783 -> Y : -1.23
  //23:17:43.783 -> Z : -7.52
  mpu6050.calcGyroOffsets(-1.35,-1.23,-7.52);

  bodyTempSensor.begin();

  tempTimer.settimer(2000);
  tempTimer.starttimer();

  mpu6050Timer.settimer(250);
  mpu6050Timer.starttimer();

  read_battery_voltage();
  voltTimer.settimer(30000);
  voltTimer.starttimer();
  
  interactTimer.settimer(5000);
  interactTimer.starttimer();

  page_monitor.show_nav_bar();
  page_monitor.show(MAIN_PAGE);

  esp32_timer_initialize();
}


void readTemperature(){
   // call sensors.requestTemperatures() to issue a global temperature
   // request to all devices on the bus
  /********************************************************************/
   //Serial.print(" Requesting temperatures...");
   bodyTempSensor.requestTemperatures(); // Send the command to get temperature readings
   //Serial.println("DONE");
  /********************************************************************/
   //Serial.print("Temperature is: ");
   bodyTemp = bodyTempSensor.getTempCByIndex(0);
   avgBodyTemp += bodyTemp;
   //Serial.print(bodyTemp);
   //Serial.println();
}

void readMPU6050(){
  mpu6050.update();

  if(mpu6050Timer.checkfinish()){

    //Serial.println("=======================================================");
    //Serial.print("temp : ");Serial.println(mpu6050.getTemp());
    acc[0] = mpu6050.getAccX();
    acc[1] = mpu6050.getAccY();
    acc[2] = mpu6050.getAccZ();
    if (pack_counter < 4){
      datapack[pack_counter].set_acc(acc);
      pack_counter++;
    }
    //Serial.print("accX : ");Serial.print(acc[0]);
    //Serial.print("\taccY : ");Serial.print(acc[1]);
    //Serial.print("\taccZ : ");Serial.println(acc[2]);

    //Serial.print("gyroX : ");Serial.print(mpu6050.getGyroX());
    //Serial.print("\tgyroY : ");Serial.print(mpu6050.getGyroY());
    //Serial.print("\tgyroZ : ");Serial.println(mpu6050.getGyroZ());

    //Serial.print("accAngleX : ");Serial.print(mpu6050.getAccAngleX());
    //Serial.print("\taccAngleY : ");Serial.println(mpu6050.getAccAngleY());

    //gyr[0] = mpu6050.getGyroAngleX();
    //gyr[1] = mpu6050.getGyroAngleY();
    //gyr[2] = mpu6050.getGyroAngleZ();

    //Serial.print("gyroAngleX : ");Serial.print(gyr[0]);
    //Serial.print("\tgyroAngleY : ");Serial.print(gyr[1]);
    //Serial.print("\tgyroAngleZ : ");Serial.println(gyr[2]);

    //Serial.print("angleX : ");Serial.print(mpu6050.getAngleX());
    //Serial.print("\tangleY : ");Serial.print(mpu6050.getAngleY());
    //Serial.print("\tangleZ : ");Serial.println(mpu6050.getAngleZ());
    //Serial.println("=======================================================\n");



    mpu6050Timer.resettimer();
    mpu6050Timer.starttimer();
  }
}

void send_body_data_2_firebase(){

  FirebaseJson json_data;
  json_data.add("body", avgBodyTemp/bodyTempCount);
  json_data.add("move_type", correct_move_type);
  if (Firebase.pushJSON(firebaseData, firebase_body_data_address, json_data))
  {
    Serial.println("PUSHED body_data");
  }
  else
  {
    Serial.println("FAILED");
    Serial.println("REASON: " + firebaseData.errorReason());
    Serial.println("------------------------------------");
    Serial.println();
  }
}

void check_is_send_2_firebase(){
  Firebase.getBool(firebaseData, firebase_start_send, isSendData2Firebase);
}

void send_data_2_firebase(){
  FirebaseJsonArray json_array;
  for (int i = 0 ; i < 4; i++){
    FirebaseJson json_data;
    datapack[i].set_json_data(&json_data, correct_move_type);
    json_array.set(i, json_data);
  }
  
  if (Firebase.pushArray(firebaseData, firebase_sensor_address, json_array))
  {
    Serial.println("PUSHED");
  }
  else
  {
    Serial.println("FAILED");
    Serial.println("REASON: " + firebaseData.errorReason());
    Serial.println("------------------------------------");
    Serial.println();
  }
}

void loop()
{
  //read_time();
  if (voltTimer.checkfinish()){
  //  read_battery_voltage();
    voltTimer.resettimer();
    voltTimer.starttimer();
  }
  
  if (button_monitor.check_trigger(&page_monitor)){
    interactTimer.resettimer();
    interactTimer.starttimer();
  }


  if (tempTimer.checkfinish()){
    readTemperature();
    bodyTempCount ++;
    tempTimer.resettimer();
    tempTimer.starttimer();
  }
  
  readMPU6050();

  page_monitor.update();

  if (interactTimer.checkfinish() && interactTimer.checkCounting()){
    //Serial.println();
    //Serial.print("sleep");
    //Serial.println();
    page_monitor.show(EMPTY_PAGE);
    interactTimer.resettimer();
  }

  check_is_send_2_firebase();

  if (interruptCounter > 0) {
    portENTER_CRITICAL(&timerMux);
    interruptCounter--;
    portEXIT_CRITICAL(&timerMux);
 
    if (isSendData2Firebase)
      totalInterruptCounter++;
    else
      totalInterruptCounter = SEND_PERIOD-3;

    Firebase.getString(firebaseData, firebase_watch_move_type, correct_move_type);
    send_data_2_firebase();
    pack_counter = 0;

    if (totalInterruptCounter % SEND_PERIOD == 0){
      if (isSendData2Firebase)
        send_body_data_2_firebase();
      avgBodyTemp = 0;
      bodyTempCount = 0;
      totalInterruptCounter = 0;
    }
    
    //Serial.print("An interrupt as occurred. Total number: ");
    //Serial.println(totalInterruptCounter);
  }

}
