from libs import realtime_firebase as rt
from libs import ac_firebase_remote as ac_remote
import random
import datetime



class AC_host:

    def __init__(self, ac_serial_num, watch_serial_num):
        self.db = rt.Realtime_firebase()
        self.remote = ac_remote.AC_remote()
        self.base_ac_path = "Devices/" + ac_serial_num
        self.base_watch_path = "Devices" + watch_serial_num
        self.reset()

    def reset(self):
        self.current_step = 0
        self.ac_sensor_data_counter = 0
        self.watch_sensor_data_counter = 0
        self.power_state = self.db.get(self.base_ac_path+"/ac_status", is_dict=True)['power_state']
        self.set_temperature = self.db.get(self.base_ac_path+"/ac_status", is_dict=True)['set_temp']
        self.set_fanspeed = self.db.get(self.base_ac_path+"/ac_status", is_dict=True)['set_fanspeed']


    def generate_control_pair(self):
        temp_action_value = random.randint(0,len(ac_remote.Actions_Temp)-1)
        fanspeed_action_value = random.randint(0, len(ac_remote.Actions_Fanspeed)-1)
        temp_func, temp, fan_func, fanspeed = self.remote.get_value_pair(temp_action_value, fanspeed_action_value)
        return [(temp_func,temp), (fan_func, fanspeed)]


    def generate_command(self, name, value):
        if (name == "temp"):
            return self.remote.get_action_command(temp=value)
        elif (name == "fanspeed"):
            return self.remote.get_action_command(fanspeed=value)
        else:
            return None


    def send_control_command(self, command):
        # send the command to the firebase, in firebase, True value = true
        self.db.set(self.base_ac_path, "receive_action", {'command':command,'is_new_action':true})


    def read_action_done(self):
        # read the is_new_action
        pack = self.db.get(self.base_ac_path+"/receive_action", is_dict = True)
        return not(pack.get('is_new_action', True))


    def collect_data(self):
        env_data = self.db.get(self.base_ac_path+"/sensors").pop()
        body_data = self.db.get(self.base_watch_path+"/datapack").pop()
        feedback_data = self.db.get(self.base_ac_path+"/feedback").pop()
        return {**env_data, **body_data}


    def push_data(self, data):
        self.db.add(self.base_ac_path+"/datapack", data)


    def check_new_data(self):
        if ():


host = AC_host("fyp0001","watch0001")
host.generate_control_pair()
print(host.read_action_done())
currentDT = datetime.datetime.now()
print (str(currentDT))
