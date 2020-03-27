from libs import realtime_firebase as rt
from libs import ac_firebase_remote as ac_remote
from libs.timer import Timer
import datetime
import random
import datetime
import sys
import requests


class AC_host:

    def __init__(self, ac_serial_num, watch_serial_num):
        self.db = rt.Realtime_firebase()
        self.remote = ac_remote.AC_remote()
        self.base_ac_path = "Devices/" + ac_serial_num
        self.base_watch_path = "Devices/" + watch_serial_num
        self.weather_api_address = "http://api.openweathermap.org/data/2.5/weather?q=HongKong,hk&appid=2012d486d411dabe6c1e94eeec8eedb6"
        self.period = 10
        self.data_request_period = 30
        self.reset()

    def reset(self):
        self.current_step = 0
        self.update_ac_status()
        self.db.set(self.base_ac_path,"receive_action", {'is_new_action': False, 'current_step':0})


    def generate_control_pair(self):
        done = False
        while (not done):
            temp_action_value = random.randint(0,len(ac_remote.Actions_Temp)-1)
            fanspeed_action_value = random.randint(0, len(ac_remote.Actions_Fanspeed)-1)
            temp_func, temp, fan_func, fanspeed = self.remote.get_value_pair(temp_action_value, fanspeed_action_value)
            if (temp != self.set_temperature and fanspeed != self.set_fanspeed):
                if (abs(temp-self.set_temperature) <= 3):
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


    def set_is_learning(self, flag):
        self.db.set(self.base_ac_path, "receive_action", {'is_learning':flag})


    def get_is_learning(self):
        # read the is_new_action
        pack = self.db.get(self.base_ac_path+"/receive_action", is_dict=True)
        flag = pack['is_learning']
        return flag


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
        weather_data = self.get_weather_data()
        return {**env_data, **body_data, **feedback_data, **action_data, **weather_data}


    def push_data(self, data):
        self.db.add(self.base_ac_path+"/datapack", data)


    def send_new_data_requestion(self):
        self.db.set(self.base_ac_path, "receive_action", {'is_send' : True})
        self.db.set(self.base_watch_path, "receive_action", {'is_send' : True})


    def check_has_new_data(self):
        ac_send = self.db.get(self.base_ac_path+"/receive_action", is_dict=True)['is_send']
        watch_send = self.db.get(self.base_watch_path+"/receive_action", is_dict=True)['is_send']
        if (ac_send is False and watch_send is False):
            return True
        else:
            return False


    def update_step_no(self):
        self.db.set(self.base_ac_path, "receive_action", {'current_step':self.current_step})


    def ac_power_switch(self, isSwitchOn):
        command = self.remote.get_action_command(power_state=isSwitchOn)
        self.send_control_command(command)


    def get_weather_data(self):
        json_data = requests.get(self.weather_api_address).json()
        weather_pack = {
                        'outdoor_temp':(json_data['main']['temp']-273.15),
                        'outdoor_hum':json_data['main']['humidity'],
                        'outdoor_press':(json_data['main']['pressure']/10),
                        'outdoor_des':json_data['weather'][0]['description']
                        }
        return weather_pack


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
        data_request_timer = Timer()
        data_request_timer.start()
        host.set_is_learning(True)
        while(host.power_state):
            if (data_request_timer.check() > host.data_request_period):
                host.send_new_data_requestion()
                data_request_timer.stop()
                while (not host.check_has_new_data()):
                    pass

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
                data_request_timer.start()
                data_pkg = host.collect_data()
                host.push_data(data_pkg)
                print(f'Step: {host.current_step+1} {data_pkg}')
                host.current_step += 1
                host.update_step_no()

                if (host.get_is_learning() is False):
                    if (host.check_action_done()):
                        host.ac_power_switch(False)
                    print("Waiting AC Remote respoonse")
                    while(not host.check_action_done()):
                        pass
                    host.update_ac_status()
                    print("AC is switched OFF")


    print(f"Section has {host.current_step} steps.", end=" ")
    overall_timer.stop(show=True)




'''
host.generate_control_pair()
print(host.read_action_done())
currentDT = datetime.datetime.now()
print (str(currentDT))
print(host.check_has_new_data())
'''
