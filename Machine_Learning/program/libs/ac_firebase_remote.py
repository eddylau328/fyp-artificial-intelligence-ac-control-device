#import realtime_firebase as rt
import enum

class Actions(enum.Enum):
    temp_25 = 0
    temp_24 = 1
    temp_23 = 2
    temp_22 = 3
    temp_21 = 4
    temp_20 = 5
    temp_19 = 6
    temp_18 = 7
    temp_17 = 8


class AC_remote:

    def __init__(self, serial_num):
        self.set_temperature = 24
        self.set_fanspeed = 1
        self.power_state = False


    def get_value_pair(self, action_value):
        name = Actions(action_value).name
        return name.split('_')[0], int(name.split('_')[1])


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
    remote = AC_remote("fyp0001")
    print(remote.get_value_pair(0))
    func, value = remote.get_value_pair(0)
    print(remote.get_action_command(temp=value))
    '''
    r = rt.Realtime_firebase()
    remote = AC_remote("fyp0001")
    command = ""
    command = input()
    while (command != "quit"):
        if (r.set("/Devices/fyp0001","receive_action",{"command":command, "is_new_action": True})):
            print("Sent command to firebase")
        command = input()
    '''
