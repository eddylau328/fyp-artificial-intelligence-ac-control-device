#include <Wire.h>
#include "MAX30105.h"

#include <MPU6050_tockn.h>

#include "heartRate.h"

#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <Timer.h>

#include <OneWire.h>
#include <DallasTemperature.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define LOGO_HEIGHT   64
#define LOGO_WIDTH    128
// 'pepe_oled', 128x64px
const unsigned char logo_bmp [] PROGMEM = {
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


#define TEXT_HEIGHT   60
#define TEXT_WIDTH    106
const unsigned char displayText [] PROGMEM = {
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
float bodyTemp;

int acc[3] = {0,0,0};
int gyr[3] = {0,0,0};

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

#define INITIAL_PAGE 0
#define MAIN_PAGE 1
#define TEMP_PAGE 2
#define MOVE_PAGE 3
#define MENU_PAGE 4

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

    void display_logo() {
      oled->drawBitmap(
      (oled->width()  - LOGO_WIDTH ) / 2,
      (oled->height() - LOGO_HEIGHT) / 2,
      logo_bmp, LOGO_WIDTH, LOGO_HEIGHT, 1);
      oled->display();
    }

    void display_text(String text, int x, int y, bool isClear) {
      if (isClear)
        clear();
    
      oled->setTextSize(1);             // Normal 1:1 pixel scale
      oled->setTextColor(SSD1306_WHITE);        // Draw white text
      oled->setCursor(x,y);             // Start at top-left corner
      oled->println(text);
      oled->display();
    }
    
    void display_text(String text, int x, int y, bool isClear, int text_size) {
      if (isClear)
        clear();
    
      oled->setTextSize(text_size);             // Normal 1:1 pixel scale
      oled->setTextColor(SSD1306_WHITE);        // Draw white text
      oled->setCursor(x,y);             // Start at top-left corner
      oled->println(text);
      oled->display();
    }
    
    void display_text_pic() {
      oled->drawBitmap(
        (oled->width()  -  TEXT_WIDTH) / 2,
        (oled->height() - TEXT_HEIGHT) / 2,
        displayText, TEXT_WIDTH, TEXT_HEIGHT, 1);
      oled->display();
    }
    
    void clear_text(String text, int x, int y, int text_size){
      oled->setTextSize(text_size);             // Normal 1:1 pixel scale
      oled->setTextColor(SSD1306_BLACK);        // Draw white text
      oled->setCursor(x,y);             // Start at top-left corner
      oled->println(text);
      oled->display();
    }

    void draw_pixel(int x, int y){
        // Draw a single pixel in white
        oled->drawPixel(x, y, SSD1306_WHITE);
        // Show the display buffer on the screen. You MUST call display() after
        // drawing commands to make them visible on screen!
        oled->display();
    }

    void clear(int x, int y){
      oled->drawPixel(x, y, SSD1306_BLACK);
    }
    
    void clear(){
      oled->clearDisplay();
    }
    
};

class Page{
  public:
    int page_num;
        
    virtual void show(OLED oled){}
    virtual void set_page_num(int page_num){};
};

class InitialPage: public Page{
  public:

    void show(OLED oled){
      for (int i = 0; i < 6; i++){
        oled.draw_pixel(10+i*5, 32);
        delay(500);
      }
      oled.clear();
      
      oled.display_text("Welcome back, Eddy!", 0, 32, true);
      delay(2000);
      
      oled.clear();
      oled.display_text_pic();
      delay(3000);
      
      oled.clear();
      oled.display_logo();
      delay(3000);
      
      oled.clear();
    }

    void set_page_num(int page_num){
      this->page_num = page_num;
    }
};

class PageMonitor{
  private:
    Page *pages;
    int current_page = -1;
    int total_page = 0;
    OLED *oled;
    
  public:
    void set(OLED *oled, Page *pages, int total_page){
      this->oled = oled;
      this->pages = pages;
      this->total_page = total_page;
      current_page = 0;
    }

    void show(int page_num){
      switch (page_num){
        case 0:
          pages[0].show(*oled);
          break;
      }
    }
};

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

void oledDisplaySetup(){
  //oledDisplayText("Eddy FYP", 0, 0, false,2);
  //oledDisplayText("BMP: ", 0, 22, false, 1);
  //oledDisplayText("TMP: ", 0, 32, false, 1);
  //oledDisplayText("Ang: ", 0, 42, false, 1);
  //oledDisplayText("Acc: ", 0, 52, false, 1);
}

PageMonitor page_monitor;
Page *page;
InitialPage initial_page;

void setup()
{
  Serial.begin(115200);
  Serial.println("Initializing...");

  page = &initial_page;

  page_monitor.set(new OLED(&display), page, 1);

  page_monitor.show(INITIAL_PAGE);
  
  heartRateSensorSetup();

  Wire.begin();
  mpu6050.begin();

// 21:47:15.290 -> X : 1.63
// 21:47:15.290 -> Y : 0.43
// 21:47:15.290 -> Z : -2.67

  mpu6050.calcGyroOffsets(1.63,0.43,-2.67);

  bodyTempSensor.begin(); 
  
  tempTimer.settimer(2000);
  tempTimer.starttimer();

  mpu6050Timer.settimer(1000);
  mpu6050Timer.starttimer();  
}

String lastStrBeatAvg = "";
String strBeatAvg;
String lastStrTemp = "";
String strTemp;

String strAcc;
String strGyr;
String laststrAcc;
String laststrGyr;
/*
void oledDisplayLoop(){
  if (lastStrBeatAvg != strBeatAvg){
    oledClearText(lastStrBeatAvg,30, 22, 1);
    oledDisplayText(strBeatAvg, 30, 22, false, 1);
  }
  lastStrBeatAvg = strBeatAvg;

  if (lastStrTemp != strTemp){
    oledClearText(lastStrTemp,30, 32, 1);
    oledDisplayText(strTemp, 30, 32, false, 1);    
  }
  lastStrTemp = strTemp;

  if (laststrGyr != strGyr){
    oledClearText(laststrGyr,30, 42, 1);
    oledDisplayText(strGyr, 30, 42, false, 1);    
  }
  laststrGyr = strGyr;

  if (laststrAcc != strAcc){
    oledClearText(laststrAcc,30, 52, 1);
    oledDisplayText(strAcc, 30, 52, false, 1);    
  }
  laststrAcc = strAcc;
  
}
*/
void readTemperature(){
   // call sensors.requestTemperatures() to issue a global temperature 
   // request to all devices on the bus 
  /********************************************************************/
   //Serial.print(" Requesting temperatures..."); 
   bodyTempSensor.requestTemperatures(); // Send the command to get temperature readings 
   //Serial.println("DONE"); 
  /********************************************************************/
   Serial.print("Temperature is: ");
   bodyTemp = bodyTempSensor.getTempCByIndex(0);
   strTemp = String(bodyTemp);
   Serial.print(bodyTemp);
   
}

void readMPU6050(){
  mpu6050.update();

  if(mpu6050Timer.checkfinish()){
    
    Serial.println("=======================================================");
    //Serial.print("temp : ");Serial.println(mpu6050.getTemp());
    acc[0] = (int)(mpu6050.getAccX()*9.81);
    acc[1] = (int)(mpu6050.getAccY()*9.81);
    acc[2] = (int)(mpu6050.getAccZ()*9.81);
    Serial.print("accX : ");Serial.print(acc[0]);
    Serial.print("\taccY : ");Serial.print(acc[1]);
    Serial.print("\taccZ : ");Serial.println(acc[2]);
  
    //Serial.print("gyroX : ");Serial.print(mpu6050.getGyroX());
    //Serial.print("\tgyroY : ");Serial.print(mpu6050.getGyroY());
    //Serial.print("\tgyroZ : ");Serial.println(mpu6050.getGyroZ());
  
    //Serial.print("accAngleX : ");Serial.print(mpu6050.getAccAngleX());
    //Serial.print("\taccAngleY : ");Serial.println(mpu6050.getAccAngleY());

    gyr[0] = (int)mpu6050.getGyroAngleX();
    gyr[1] = (int)mpu6050.getGyroAngleY();
    gyr[2] = (int)mpu6050.getGyroAngleZ();
  
    Serial.print("gyroAngleX : ");Serial.print(gyr[0]);
    Serial.print("\tgyroAngleY : ");Serial.print(gyr[1]);
    Serial.print("\tgyroAngleZ : ");Serial.println(gyr[2]);
    
    //Serial.print("angleX : ");Serial.print(mpu6050.getAngleX());
    //Serial.print("\tangleY : ");Serial.print(mpu6050.getAngleY());
    //Serial.print("\tangleZ : ");Serial.println(mpu6050.getAngleZ());
    Serial.println("=======================================================\n");

    strGyr = "(" + String(gyr[0]) + "," + String(gyr[1]) + "," + String(gyr[2]) + ")";
    strAcc = "(" + String(acc[0]) + "," + String(acc[1]) + "," + String(acc[2]) + ")";
    
    mpu6050Timer.resettimer();
    mpu6050Timer.starttimer();
  }
}

void loop()
{
  /*
  if (tempTimer.checkfinish()){
    readTemperature();
    tempTimer.resettimer();
    tempTimer.starttimer();
  }
  
  long irValue = particleSensor.getIR();
  if (checkForBeat(irValue) == true)
  {
    //We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
      rates[rateSpot++] = (byte)beatsPerMinute; //Store this reading in the array
      rateSpot %= RATE_SIZE; //Wrap variable

      //Take average of readings
      beatAvg = 0;
      for (byte x = 0 ; x < RATE_SIZE ; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }  
  
  Serial.print("IR=");
  Serial.print(irValue);
  Serial.print(", BPM=");
  Serial.print(beatsPerMinute);
  Serial.print(", Avg BPM=");
  Serial.print(beatAvg);
  
  
  if (irValue < 50000){
  //  Serial.print(" No finger?");
    strBeatAvg = "No finger";
  }
  else {
    strBeatAvg = String(beatAvg);
  }  
  
  Serial.println();

  readMPU6050();

  oledDisplayLoop();
  */
}
