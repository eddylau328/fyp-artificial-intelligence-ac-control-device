#import realtime_firebase as rt
import enum

class Actions_Temp(enum.Enum):
    temp_25 = 0
    temp_24 = 1
    temp_23 = 2
    temp_22 = 3
    temp_21 = 4
    temp_20 = 5
    temp_19 = 6
    temp_18 = 7
    temp_17 = 8


class Actions_Fanspeed(enum.Enum):
    fanspeed_1 = 0
    fanspeed_2 = 1
    fanspeed_3 = 2


class AC_remote:

    def __init__(self):
        self.set_temperature = 24
        self.set_fanspeed = 1
        self.power_state = False


    def get_fanspeed_value_pair(self, fanspeed_action_value):
        name = Actions_Fanspeed(fanspeed_action_value).name
        return name.split('_')[0], int(name.split('_')[1])


    def get_temp_value_pair(self, temp_action_value):
        name = Actions_Temp(temp_action_value).name
        return name.split('_')[0], int(name.split('_')[1])


    def get_value_pair(self, temp_action_value, fanspeed_action_value):
        temp_name, temp_value = self.get_temp_value_pair(temp_action_value)
        fan_name, fan_value = self.get_fanspeed_value_pair(fanspeed_action_value)
        return temp_name, temp_value, fan_name, fan_value


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


'''
if (__name__ == '__main__'):
    r = rt.Realtime_firebase()
    remote = AC_remote()
    command = ""
    command = input()
    while (command != "quit"):
        if (r.set("/Devices/fyp0001","receive_action",{"command":command, "is_new_action": True})):
            print("Sent command to firebase")
        command = input()
'''
