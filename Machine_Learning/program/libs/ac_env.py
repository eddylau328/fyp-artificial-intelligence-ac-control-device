import gym
import numpy as np
import enum
from libs import realtime_firebase as rt
from libs import ac_firebase_remote as ac_remote
from gym import spaces
import json
from datetime import datetime

MAX_REWARD = 96
MAX_STEPS = 24   # for 5 minutes section, 5 min each step, total 24 steps, 2 hours
MAX_MIN = (28.600000381, 23.399999619, 85.300003052, 43.200000763, 34.259998322, 30.6875)

MAX_TEMP_DROP = {
    '17': 19.5,
    '18': 20.0,
    '19': 21.5,
    '20': 22.0,
    '21': 22.5,
    '22': 23.5,
    '23': 24.0,
    '24': 25.0,
    '25': 26.0
}


def num_of_paths():
    i = 1
    found = False
    while (not found):
        filepath = 'env_training_data/env_data_'+str(i)
        try:
            with open(filepath +'.json', 'r') as file:
                i += 1
                # Do something with the file
        except IOError:
            found = True
    return i-1

def get_data(path, dataname):
    with open(path, 'r') as file:
        json_file = json.load(file)
    return json_file[dataname]

def feedback_mark(feedback,set_temp,set_fanspeed,isChangeTemp,isChangeFan,indoor_temp,previous_temp):
    mark = 0
    if (feedback == "comfy"):
        mark += 5
    elif (feedback == "a bit hot" or feedback == "a bit cold"):
        mark -= 1
    elif (feedback == "hot" or feedback == "cold"):
        mark -= 2
    else:
        mark -= 3

    # set_temp range
    if (set_temp <= 17):
        mark -= 2.5
    # [18,19]
    elif (set_temp <= 19):
        mark -= 2
    # [20,21]
    elif (set_temp <= 21):
        mark -= 1.5
    # [22,23]
    elif (set_temp <= 23):
        mark -= 1
    # [24,25]
    else:
        mark -= 0.5

    if (set_fanspeed <= 1):
        mark -= 0.5
    elif (set_fanspeed <= 2):
        mark -= 1
    else:
        mark -= 1.5

    # prevent no using all the cooling power
    if (isChangeTemp and indoor_temp > MAX_TEMP_DROP[str(previous_temp)]):
        mark -= 2*(indoor_temp-MAX_TEMP_DROP[str(previous_temp)])

    # don't want it to rely on low temperature cooling
    if (isChangeTemp):
        if (set_temp - previous_temp >= 6):
            mark -= 6
        elif (set_temp - previous_temp >= 4):
            mark -= 4
        elif (set_temp - previous_temp >= 2):
            mark -= 2

    return mark


class Actions(enum.Enum):
    temp_17_fanspeed_1 = 0
    temp_17_fanspeed_2 = 1
    temp_17_fanspeed_3 = 2
    temp_18_fanspeed_1 = 3
    temp_18_fanspeed_2 = 4
    temp_18_fanspeed_3 = 5
    temp_19_fanspeed_1 = 6
    temp_19_fanspeed_2 = 7
    temp_19_fanspeed_3 = 8
    temp_20_fanspeed_1 = 9
    temp_20_fanspeed_2 = 10
    temp_20_fanspeed_3 = 11
    temp_21_fanspeed_1 = 12
    temp_21_fanspeed_2 = 13
    temp_21_fanspeed_3 = 14
    temp_22_fanspeed_1 = 15
    temp_22_fanspeed_2 = 16
    temp_22_fanspeed_3 = 17
    temp_23_fanspeed_1 = 18
    temp_23_fanspeed_2 = 19
    temp_23_fanspeed_3 = 20
    temp_24_fanspeed_1 = 21
    temp_24_fanspeed_2 = 22
    temp_24_fanspeed_3 = 23
    temp_25_fanspeed_1 = 24
    temp_25_fanspeed_2 = 25
    temp_25_fanspeed_3 = 26

class AC_Env(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes' : ['human']}

    def __init__(self, isSimulate, host, thermal_predict_model, temperature_prediction_model, humidity_predicition_model, skin_temperature_prediction_model):
        super(AC_Env, self).__init__()

        self.df = None
        self.database = rt.Realtime_firebase()
        self.ac_remote = ac_remote.AC_remote()
        self.reward_range = (0, MAX_REWARD)
        self.reward = 0
        self.action = 0
        self._max_episode_steps = MAX_STEPS
        self.total_reward = 0
        #temperature, humidity,outdoor temp, outdoor humidity, body temperature
        obersavtion_high = np.array([30.0, 100.0, 30.0, 100.0, 35.0])
        obersavtion_low  = np.array([15.0, 30.0,  15.0, 20.0,  29.0])
        self.observation_space = spaces.Box(low=obersavtion_low, high=obersavtion_high)
        self.action_space = spaces.Discrete(n=len(Actions))
        self.isSimulate = isSimulate
        self.previous_action = None
        self.host = host
        self.current_data_pkg = None
        self.previous_data_pkg = None
        self.thermal_prediction_model = thermal_predict_model
        self.temperature_prediction_model = temperature_prediction_model
        self.humidity_predicition_model = humidity_predicition_model
        self.skin_temperature_prediction_model = skin_temperature_prediction_model


    def _next_observation(self):
        if (self.isSimulate == False):
            pass
            # send data request
            #self.host.send_new_data_requestion()
            # wait until the sensor get the data
            #while (not self.host.check_has_new_data()):
            #    pass
            #self.data_pkg = self.host.collect_data()
            #obs = np.array([self.data_pkg['temp'],self.data_pkg['hum'], self.data_pkg['outdoor_temp'], self.data_pkg['outdoor_hum'], self.data_pkg['body']])
        else:
            if (self.current_step == 0):
                datapack = []
                for i in range(1, num_of_paths()+1):
                    datapack.append(get_data('env_training_data/env_data_'+str(i)+'.json', 'datapack'))
                for pack in datapack:
                    avg_outdoor_temp, avg_outdoor_hum = 0.0, 0.0
                    for dict_obj in pack:
                        avg_outdoor_temp += dict_obj['outdoor_temp']
                        avg_outdoor_hum += dict_obj['outdoor_hum']
                    avg_outdoor_temp = avg_outdoor_temp / len(pack)
                    avg_outdoor_hum = avg_outdoor_hum / len(pack)
                    for dict_obj in pack:
                        dict_obj['outdoor_temp'] = avg_outdoor_temp
                        dict_obj['outdoor_hum'] = avg_outdoor_temp

                data = []
                for pack in datapack:
                    for dict_obj in pack:
                        data.append(dict_obj)
                pkg_list = []
                for i in range(len(data)):
                    pair = []
                    if(data[i]['stepNo'] < 5):
                        pair.append([data[i]['temp'],data[i]['hum'],
                            data[i]['outdoor_temp'],data[i]['outdoor_hum'],
                            data[i]['body'],24,1,data[i]['time']])
                        pair.append([data[i+1]['temp'],data[i+1]['hum'],
                            data[i+1]['outdoor_temp'],data[i+1]['outdoor_hum'],
                            data[i+1]['body'],24,1,data[i+1]['time']])
                        pkg_list.append(pair)
                pkg_list = np.array(pkg_list)
                selection = np.random.choice(pkg_list.shape[0], 1)
                pkg = pkg_list[selection].reshape(2,8).tolist()
                pkg_dict = []
                for value in pkg:
                    pkg_dict.append({
                        'temp' : float(value[0]),
                        'hum' : float(value[1]),
                        'outdoor_temp' : float(value[2]),
                        'outdoor_hum' : float(value[3]),
                        'body' : float(value[4]),
                        'set_temp' : int(value[5]),
                        'set_fanspeed': int(value[6]),
                        'time' : value[7]
                    })
                str_pre_time, str_curr_time = pkg_dict[0]['time'], pkg_dict[1]['time']
                pre_time = datetime.strptime(str_pre_time, '%Y-%m-%d %H:%M:%S.%f')
                curr_time = datetime.strptime(str_curr_time, '%Y-%m-%d %H:%M:%S.%f')
                predict_delta_time = (curr_time-pre_time).seconds + 30.0
                predict_temp = self.temperature_prediction_model.predict(pkg_dict, predict_delta_time)
                predict_hum = self.humidity_predicition_model.predict(pkg_dict, predict_delta_time)
                predict_body = self.skin_temperature_prediction_model.predict(pkg_dict, predict_delta_time)
                outdoor_temp, outdoor_hum = pkg_dict[1]['outdoor_temp'], pkg_dict[1]['outdoor_hum']
                self.previous_data_pkg = {
                    'temp': pkg_dict[1]['temp'],
                    'hum': pkg_dict[1]['hum'],
                    'outdoor_temp': pkg_dict[1]['outdoor_temp'],
                    'outdoor_hum': pkg_dict[1]['outdoor_hum'],
                    'set_temp' : pkg_dict[1]['set_temp'],
                    'set_fanspeed': pkg_dict[1]['set_fanspeed'],
                    'body': pkg_dict[1]['body']
                }
                self.current_data_pkg = {
                    'temp': predict_temp,
                    'hum': predict_hum,
                    'outdoor_temp': outdoor_temp,
                    'outdoor_hum': outdoor_hum,
                    'body': predict_body
                }
                obs = np.array([self.current_data_pkg['temp'],self.current_data_pkg['hum'], self.current_data_pkg['outdoor_temp'], self.current_data_pkg['outdoor_hum'], self.current_data_pkg['body']])
            else:
                for i in range(10):
                    pkg = [self.previous_data_pkg, self.current_data_pkg]
                    predict_delta_time = 60.0   # previous + predict = 30s + 30s = 60s
                    predict_temp = self.temperature_prediction_model.predict(pkg, predict_delta_time)
                    predict_hum = self.humidity_predicition_model.predict(pkg, predict_delta_time)
                    predict_body = self.skin_temperature_prediction_model.predict(pkg, predict_delta_time)
                    outdoor_temp, outdoor_hum = self.current_data_pkg['outdoor_temp'], self.current_data_pkg['outdoor_hum']
                    self.previous_data_pkg = self.current_data_pkg
                    self.current_data_pkg = {
                        'temp': predict_temp,
                        'hum': predict_hum,
                        'outdoor_temp': outdoor_temp,
                        'outdoor_hum': outdoor_hum,
                        'body': predict_body,
                        'set_temp':self.previous_data_pkg['set_temp'],
                        'set_fanspeed':self.previous_data_pkg['set_fanspeed']
                    }
                obs = np.array([self.current_data_pkg['temp'],self.current_data_pkg['hum'], self.current_data_pkg['outdoor_temp'], self.current_data_pkg['outdoor_hum'], self.current_data_pkg['body']])
        return obs


    def _take_action(self, action):
        if (not self.isSimulate):
            action_name = Actions(action).name.split('_')
            temp, fanspeed = int(action_name[1])-17, int(action_name[3])-1
            control_pair = self.host.generate_control_pair(input_temp=temp, input_fanspeed=fanspeed)
            command = self.host.generate_command('temp', control_pair['temp'])
            self.host.send_control_command(command)
            while (not self.host.check_action_done()):
                pass
            command = self.host.generate_command('fanspeed', control_pair['fanspeed'])
            self.host.send_control_command(command)
            while (not self.host.check_action_done()):
                pass
        self.host.update_ac_status()


    def step(self, action):
        self._take_action(action)
        self.action = action
        isChangeTemp, isChangeFan = False, False
        previous_temp, previous_fanspeed = 0, 0
        if (self.current_step != 0):
            action_name = Actions(action).name.split('_')
            temp, fanspeed = int(action_name[1]), int(action_name[3])
            previous_action_name = Actions(self.previous_action).name.split('_')
            previous_temp, previous_fanspeed = int(previous_action_name[1]), int(previous_action_name[3])
            if (previous_temp != temp):
                isChangeTemp = True
            if (previous_fanspeed != fanspeed):
                isChangeFan = True

        self.previous_action = self.action
        # update the current data package # Important
        self.current_data_pkg['set_temp'] = self.host.set_temperature
        self.current_data_pkg['set_fanspeed'] = self.host.set_fanspeed
        # return a dictionary, input key to get feedback value
        feedback = self.host.get_feedback()
        feedback = feedback['feedback']
        feedback = feedback.replace(' ','_').lower()
        # no feedback directly from the user
        # call supervised learning model to estimate the user thermal comfort levels
        if (feedback == "acceptable"):
            feedback = self.thermal_prediction_model.predict(self.current_data_pkg)

        delay_modifier = (self.current_step / MAX_STEPS)
        self.reward = feedback_mark(feedback, set_temp=self.host.set_temperature, set_fanspeed=self.host.set_fanspeed, isChangeTemp=isChangeTemp, isChangeFan=isChangeFan,indoor_temp=self.current_data_pkg['temp'],previous_temp=previous_temp) * delay_modifier
        self.total_reward += self.reward
        self.current_step += 1
        done = self.total_reward >= MAX_REWARD or self.current_step > MAX_STEPS
        if (self.current_step > MAX_STEPS):
            self.current_step = 0
        obs = self._next_observation()

        return obs, self.reward, done, {}


    def reset(self):
        self.current_step = 0
        self.reward = 0
        self.total_reward = 0
        self.previous_action = None
        self.host.reset()
        self.host.set_is_learning(True)
        return self._next_observation()


    def render(self, mode="human", close=False):
        # Render the environment to the screen
        print('Step: {:20}'.format(self.current_step), end="|")
        print('Action: set to {:20}'.format(self.action), end="|")
        print('reward: {:20}'.format(self.reward), end="|")
        print('total_reward: {:20}'.format(self.total_reward))
