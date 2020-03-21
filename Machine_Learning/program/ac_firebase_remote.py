from libs import realtime_firebase as rt


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
    while (command != "quit"):
        command = input()
        if (r.set("/Devices/fyp0001","receive_action",{"command":command, "is_new_action": True})):
            print("Sent command to firebase")
