import libs.realtime_firebase as rt
import libs.ac_firebase_remote as ac_remote
import libs.timer
import random
import datetime
import requests
import enum

class Power_Level_Temp(enum.Enum):
    temp_25 = 0
    temp_24 = 0
    temp_23 = 1
    temp_22 = 1
    temp_21 = 2
    temp_20 = 2
    temp_19 = 3
    temp_18 = 4
    temp_17 = 4

class Power_Level_Fanspeed(enum.Enum):
    fanspeed_1 = 0
    fanspeed_2 = 1
    fanspeed_3 = 2


class AC_host:

    def __init__(self, ac_serial_num, watch_serial_num, data_request_seconds=None, steps_calculation_period=None):
        self.db = rt.Realtime_firebase()
        self.remote = ac_remote.AC_remote()
        self.base_ac_path = "Devices/" + ac_serial_num
        self.base_watch_path = "Devices/" + watch_serial_num
        self.weather_api_address = "http://api.openweathermap.org/data/2.5/weather?q=HongKong,hk&appid=2012d486d411dabe6c1e94eeec8eedb6"
        self.period = 10
        if (data_request_seconds == None):
            self.data_request_seconds = 30
        else:
            self.data_request_seconds = data_request_seconds
        if (steps_calculation_period == None):
            self.steps_calculation_period = 10
        else:
            self.steps_calculation_period = steps_calculation_period
        self.reset()


    def reset(self):
        self.period = self.steps_calculation_period
        self.current_step = 0
        self.update_ac_status()
        self.db.set(self.base_ac_path,"receive_action",
            {'is_new_action': False,
             'current_step':0,
             'override_control':False,
             'is_send':False})


    def check_terminate_program(self):
        return self.db.get(self.base_ac_path+"/receive_action", is_dict=True)['terminate_program']


    def check_start_control(self):
        return self.db.get(self.base_ac_path+"/receive_action", is_dict=True)['start_control']


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

        return {temp_func:temp, fan_func:fanspeed}


    def update_period(self):
        self.period = self.current_step + self.steps_calculation_period
        print("The Next action will be taken on steps {}".format(self.period))


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
        self.db.set(self.base_ac_path, "receive_action", {'override_control': value})


    def set_override_control_setting(self, **kwargs):
        self.db.set(self.base_ac_path, "receive_action",
            {'override_power': kwargs.get('override_power', False),
             'override_set_temp': kwargs.get('override_set_temp', 24),
             'override_set_fanspeed': kwargs.get('override_set_fanspeed', 1)})


    def get_override_control_setting(self):
        pack = self.db.get(self.base_ac_path+"/receive_action", is_dict=True)
        return {'temp':pack['override_set_temp'], 'fanspeed':pack['override_set_fanspeed'], 'power':pack['override_power']}


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
        env_data = self.db.get(self.base_ac_path+"/sensors")
        if (env_data == None):
            env_data = {}
        else:
            env_data = env_data.pop()
        body_data = self.db.get(self.base_watch_path+"/datapack")
        if (body_data == None):
            body_data = {}
        else:
            body_data = body_data.pop()
        feedback_data = self.get_feedback()

        action_data = {'set_temp':self.set_temperature, 'set_fanspeed':self.set_fanspeed, 'stepNo':self.current_step, 'time':str(datetime.datetime.now())}
        weather_data = self.get_weather_data()
        return {**env_data, **body_data, **feedback_data, **action_data, **weather_data}


    def get_feedback(self):
        feedback_data = self.db.get(self.base_ac_path+"/feedback")
        if (feedback_data is None):
            feedback_data = {'feedback':"acceptable"}
        else:
            feedback_data = feedback_data.pop()
            if (feedback_data['stepNo'] != self.current_step):
                feedback_data = {'feedback':"acceptable"}
            else:
                feedback_data = {'feedback': feedback_data['feedback']}
        return feedback_data


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


    def reset_data_request(self):
        self.db.set(self.base_ac_path, "receive_action", {'is_send' : False})
        self.db.set(self.base_watch_path, "receive_action", {'is_send' : False})


    def check_devices_data_state(self):
        ac_send = self.db.get(self.base_ac_path+"/receive_action", is_dict=True)['is_send']
        watch_send = self.db.get(self.base_watch_path+"/receive_action", is_dict=True)['is_send']
        return {'ac_is_send':ac_send,'watch_is_send':watch_send}


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


    def download_data(self):
        data = self.db.extract_data(self.base_ac_path+'/datapack', get=True)
        pack = []
        if (data != None):
            for i in range(len(data)):
                if (data[i]['stepNo'] == 0):
                    pack.append(i)
        file_count = 1
        filepath = ""
        while (True):
            filepath = "env_training_data/env_data_"+str(file_count)
            try:
                with open(filepath +'.json', 'r') as file:
                    file_count += 1
                    # Do something with the file
            except IOError:
                file_count -= 1;

                break
        print("There are {} new data pack".format(len(pack)))
        print("Data will be save to:")
        for i in range(file_count+1, file_count+len(pack)+1):
            print("<env_training_data/env_data_" +str(i) + ".json>")
        for j in range(file_count+len(pack), file_count, -1):
            new_data = []
            start = pack.pop()
            for i in range(start, len(data)):
                new_data.append(data[i])
            for i in range(start, len(data)):
                data.pop()
            filename = 'env_training_data/env_data_' + str(j)
            self.db.export(data=new_data,dataname='datapack',filename=filename)
        self.db.extract_data(self.base_ac_path+'/datapack', delete=True)
        self.db.delete(self.base_ac_path+"/sensors")
        self.db.delete(self.base_watch_path+"/datapack")
