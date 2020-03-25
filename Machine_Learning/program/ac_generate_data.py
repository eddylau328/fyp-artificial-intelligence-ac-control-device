from libs import realtime_firebase as rt
from libs import ac_firebase_remote as ac_remote
from libs.timer import Timer
import datetime
import random
import datetime
import sys


class AC_host:

    def __init__(self, ac_serial_num, watch_serial_num):
        self.db = rt.Realtime_firebase()
        self.remote = ac_remote.AC_remote()
        self.base_ac_path = "Devices/" + ac_serial_num
        self.base_watch_path = "Devices" + watch_serial_num
        self.period = 6
        self.reset()

    def reset(self):
        self.current_step = 0
        self.ac_sensor_data_counter = 0
        self.watch_sensor_data_counter = 0
        self.update_ac_status()
        self.db.set(self.base_ac_path,"receive_action", {'is_new_action': False})


    def generate_control_pair(self):
        done = False
        while (not done):
            temp_action_value = random.randint(0,len(ac_remote.Actions_Temp)-1)
            fanspeed_action_value = random.randint(0, len(ac_remote.Actions_Fanspeed)-1)
            temp_func, temp, fan_func, fanspeed = self.remote.get_value_pair(temp_action_value, fanspeed_action_value)
            if (temp != self.set_temperature or fanspeed != self.set_fanspeed):
                done = True

        return {temp_func:temp, fan_func:fanspeed}


    def generate_command(self, name, value):
        if (name == "temp"):
            return self.remote.get_action_command(temp=value)
        elif (name == "fanspeed"):
            return self.remote.get_action_command(fanspeed=value)
        else:
            return None


    def send_control_command(self, command):
        self.db.set(self.base_ac_path, "receive_action", {'command':command,'is_new_action':True})


    def update_ac_status(self):
        self.power_state = self.remote.power_state
        self.set_temperature = self.remote.set_temperature
        self.set_fanspeed = self.remote.set_fanspeed


    def set_start_send_data(self, isSendData):
        self.db.set(self.base_ac_path, "receive_action", {'is_send':True})


    def check_action_done(self):
        # read the is_new_action
        pack = self.db.get(self.base_ac_path+"/receive_action", is_dict=True)
        flag = pack['is_new_action']
        return not(flag)


    def collect_data(self):
        env_data = self.db.get(self.base_ac_path+"/sensors").pop()
        body_data = self.db.get(self.base_watch_path+"/datapack").pop()
        feedback_data = self.db.get(self.base_ac_path+"/feedback")
        if (feedback_data is None):
            feedback_data = {'feedback':"acceptable"}
        else:
            feedback_data = feedback_data.pop()
        if (feedback_data['stepNo'] != self.current_step):
            feedback_data = {'feedback':"acceptable"}
        else:
            feedback_data = {'feedback': feedback_data['feedback']}

        action_data = {'set_temp':self.set_temperature, 'set_fanspeed':self.set_fanspeed, 'stepNo':self.current_step, 'time':str(datetime.datetime.now())}

        return {**env_data, **body_data, **feedback_data, **action_data}


    def push_data(self, data):
        self.db.add(self.base_ac_path+"/datapack", data)


    def check_has_new_data(self):
        env_data = self.db.get(self.base_ac_path+"/sensors")
        body_data = self.db.get(self.base_watch_path+"/datapack")
        env_data_size = len(env_data) if (env_data is not None) else 0
        body_data_size = len(body_data) if (body_data is not None) else 0
        if (env_data_size > self.ac_sensor_data_counter and body_data_size > self.watch_sensor_data_counter):
            return True
        else:
            return False


    def update_step_no(self):
        self.db.set(self.base_ac_path, "receive_action", {'current_step':self.current_step})


    def ac_power_switch(self, isSwitchOn):
        command = self.remote.get_action_command(power_state=isSwitchOn)
        self.send_control_command(command)


if (__name__ == "__main__"):
    host = AC_host("fyp0001","watch0001")

    print("Initiate Data Collection Process [Y/n]?  ", end="")
    decision = input()
    while(decision is not 'y' and decision is not 'Y' and decision is not 'n'):
        decision = input()

    overall_timer = Timer()
    overall_timer.start()
    if (decision == "y" or decision == "Y"):
        # if the AC is not yet TURN ON => TURN ON
        # else do nothing
        if (host.power_state is False):
            if (host.check_action_done()):
                host.ac_power_switch(True)
            print("Waiting AC Remote respoonse")
            while(not host.check_action_done()):
                pass
            host.update_ac_status()
            print("AC is switched ON")

        # Initiating the random action command
        # Start collecting data
        host.set_start_send_data(True)

        while(host.power_state):

            if (host.check_has_new_data()):
                if (host.current_step % host.period == 0):
                    control_pair = host.generate_control_pair()
                    command = host.generate_command('temp', control_pair['temp'])
                    host.send_control_command(command)
                    while (not host.check_action_done()):
                        pass
                    command = host.generate_command('fanspeed', control_pair['fanspeed'])
                    host.send_control_command(command)
                    while (not host.check_action_done()):
                        pass

                host.update_ac_status()
                data_pkg = host.collect_data()
                host.push_data(data_pkg)
                print(f'Step: {host.current_step+1} {data_pkg}')
                host.current_step += 1
                host.update_step_no()

        host.set_start_send_data(False)

    overall_timer.stop(show=True)




'''
host.generate_control_pair()
print(host.read_action_done())
currentDT = datetime.datetime.now()
print (str(currentDT))
print(host.check_has_new_data())
'''
