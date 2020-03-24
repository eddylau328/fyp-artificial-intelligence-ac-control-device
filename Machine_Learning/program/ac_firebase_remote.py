from libs import realtime_firebase as rt

class Actions(enum.Enum):
    Temp_25 = 0
    Temp_24 = 1
    Temp_23 = 2
    Temp_22 = 3
    Temp_21 = 4
    Temp_20 = 5
    Temp_19 = 6
    Temp_18 = 7

class AC_remote:

    def __init__(self, serial_num):
        self.set_temperature = 24
        self.set_fanspeed = 1
        self.power_state = False


    def get_action_command(self, **kwargs):
        if ('temp' in kwargs):
            if (kwargs['temp'] >= 17 and kwargs['temp'] <= 30):
                self.set_temperature = kwargs['temp']
                return "ir temp "+str(kwargs['temp'])
        elif('fanspeed' in kwargs):
            if (kwargs['fanspeed'] >= 1 and kwargs['fanspeed'] <= 4):
                self.set_fanspeed = kwargs['fanspeed']
                return "ir fanspeed "+str(kwargs['fanspeed'])
        elif('power_state' in kwargs):
            if (isinstance(kwargs['power_state'], bool)):
                self.power_state = kwargs['power_state']
                if (kwargs['power_state'] is True):
                    return "ir power on"
                else:
                    return "ir power off"


if (__name__ == '__main__'):
    r = rt.Realtime_firebase()
    remote = AC_remote("fyp0001")
    command = ""
    command = input()
    while (command != "quit"):
        if (r.set("/Devices/fyp0001","receive_action",{"command":command, "is_new_action": True})):
            print("Sent command to firebase")
        command = input()
