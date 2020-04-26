from libs import realtime_firebase as rt
from libs import ac_firebase_remote as ac_remote
from libs.timer import Timer
import supervised_learning as supervised_model
import datetime
import random
import datetime
import sys
import requests
import argparse

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
        self.override_control = False
        self.update_ac_status()
        self.db.set(self.base_ac_path,"receive_action", {'is_new_action': False, 'current_step':0})


    def generate_control_pair(self, input_temp=None, input_fanspeed=None):
        done = False
        while (not done):
            if (input_temp == None and input_fanspeed == None):
                temp_action_value = random.randint(0,len(ac_remote.Actions_Temp)-1)
                fanspeed_action_value = random.randint(0, len(ac_remote.Actions_Fanspeed)-1)
                temp_func, temp, fan_func, fanspeed = self.remote.get_value_pair(temp_action_value, fanspeed_action_value)
                if (temp != self.set_temperature and fanspeed != self.set_fanspeed):
                    if (abs(temp-self.set_temperature) <= 6):
                        done = True
                        multiplier = max(4, abs(temp-self.set_temperature))
                        self.period = random.randint(3, multiplier) * abs(temp-self.set_temperature)
            else:
                done = True
                temp_func, temp, fan_func, fanspeed = self.remote.get_value_pair(input_temp, input_fanspeed)
                self.period = 10

        return {temp_func:temp, fan_func:fanspeed}


    def generate_command(self, name, value):
        if (name == "temp"):
            return self.remote.get_action_command(temp=value)
        elif (name == "fanspeed"):
            return self.remote.get_action_command(fanspeed=value)
        else:
            return None


    def check_override_control(self):
        return self.db.get(self.base_ac_path+"/receive_action", is_dict=True)['override_control']


    def set_override_control(self, value):
        self.db.set(self.base_ac_path, "receive_action", {'override_control': False})


    def get_override_control_setting(self):
        pack = self.db.get(self.base_ac_path+"/receive_action", is_dict=True)
        return {'temp':pack['override_set_temp'], 'fanspeed':pack['override_set_fanspeed']}


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--random", default=True, help="Generate sample data for training")
    parser.add_argument("--predict",default=None, help="Control air conditioner by prediction")
    args = parser.parse_args()
    is_predict = False
    filepath = ""
    host = AC_host("fyp0001","watch0001")
    if (args.random == True and args.predict == None):
        print("Initiate Data Collection Process [Y/n]?  ", end="")
        is_predict = False
    elif (args.predict != None):
        print("Input Thermal Comfort Prediction Model : <{}>".format(args.predict))
        filepath = 'trained_models/'+args.predict
        try:
            with open(filepath, 'r') as file:
                print("filepath <{}> is exist".format(filepath))
                # Do something with the file
        except IOError:
            print("filepath <{}> is not exist".format(filepath))
            sys.exit()
        print("Initiate Thermal Comfort Prediction Process [Y/n]?  ", end="")
        is_predict = True
    else:
        sys.exit()

    decision = input()
    while(decision is not 'y' and decision is not 'Y' and decision is not 'n'):
        decision = input()

    overall_timer = Timer()
    overall_timer.start()
    if (decision == "y" or decision == "Y"):
        if (is_predict):
            model = supervised_model.create_model()
            model.load_model(filepath)
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

                data_pkg = host.collect_data()
                if (host.current_step % host.period == 0):
                    is_pass = False
                    if (host.check_override_control()):
                        control_pair = host.get_override_control_setting()
                        host.set_override_control(False)
                    else:
                        if (is_predict):
                            sorted_list = model.predict(data_pkg)
                            index = random.randint(0, 2)
                            print("Top 3 actions: {},{},{}".format(
                                (sorted_list[0][0]+17,sorted_list[0][1]+1),
                                (sorted_list[1][0]+17,sorted_list[1][1]+1),
                                (sorted_list[2][0]+17,sorted_list[2][1]+1)))
                            print("selection: {}".format((sorted_list[index][0]+17,sorted_list[index][1]+1)))
                            if (sorted_list[index][0]+17 == host.set_temperature and sorted_list[index][1]+1 == host.set_fanspeed):
                                is_pass = True
                            else:
                                is_pass = False
                            control_pair = host.generate_control_pair(input_temp=sorted_list[index][0], input_fanspeed=sorted_list[index][1])
                        else:
                            control_pair = host.generate_control_pair()
                    if (is_pass == False):
                        command = host.generate_command('temp', control_pair['temp'])
                        host.send_control_command(command)
                        while (not host.check_action_done()):
                            pass
                        command = host.generate_command('fanspeed', control_pair['fanspeed'])
                        host.send_control_command(command)
                        while (not host.check_action_done()):
                            pass
                        host.update_ac_status()
                    data_pkg['set_temp'], data_pkg['set_fanspeed'] = control_pair['temp'], control_pair['fanspeed']

                data_request_timer.start()
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
