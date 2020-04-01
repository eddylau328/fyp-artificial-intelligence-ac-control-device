import serial
import time

ser = serial.Serial(port='/dev/ttyUSB1', baudrate=9600)

try:
    ser.isOpen()
    print("Serial port is open")
except:
    print("Error")
    exit()

if (ser.isOpen()):
    try:
        while(1):
            print(ser.readline())
    except Exception:
        print("error")
else:
    print("Cannot open serial port")
