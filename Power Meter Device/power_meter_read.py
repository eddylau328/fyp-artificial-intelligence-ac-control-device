import serial

ser = serial.Serial(port='/dev/ttyUSB1', baudrate=9600)

try:
    ser.isOpen()
    print("Serial port is open")
except:
    print("Error")
    exit()

if (ser.isOpen()):
    try:
        userinput = input()
        ser.write(userinput.encode())
        while(1):
            data = ser.readline()
            if (data != None):
                print(data.decode())
                break
    except Exception:
        print("error")
else:
    print("Cannot open serial port")
