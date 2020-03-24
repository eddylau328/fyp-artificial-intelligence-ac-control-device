import gym
import numpy as np
from libs import realtime_firebase as rt
from libs import ac_firebase_remote as ac_remote
from gym import spaces

MAX_REWARD = 100
ENVIRONMENT_DATA_PATH = "Devices/fyp0001/sensors"
FEEDBACK_PATH = "Devices/fyp0001/feedback"
CHECK_FINISH_ACTION = "Devices/fyp0001/receive_action"
USER_DATA_PATH = "Devices/watch0001/datapack"
AC_REMOTE_SERIAL_NUM = "fyp0001"
MAX_STEPS = 10    # for 10 minutes section, 1 min each step, total 10 steps

def feedback_mark(feeback):
    if (feeback == "none"):
        return 0;
    elif (feedback == "comfy"):
        return 10
    elif (feedback == "a bit hot" or feedback == "a bit cold"):
        return -10
    else:
        return -20


class AC_Env(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes' : ['human']}

    def __init__(self):
        super(AC_Env, self).__init__()

        self.df = None
        self.database = rt.Realtime_firebase()
        self.ac_remote = ac_remote.AC_remote(AC_REMOTE_SERIAL_NUM)
        self.reward_range = (0, MAX_REWARD)
        self.reward = 0
        self.action = 0
        self.total_reward = 0
        #temperature, humidity, body temperature, type_of_move
        obersavtion_high = np.array([40.0, 100.0, 40.0, 3])
        obersavtion_low = np.array([15.0, 0.0, 25.0, 1])
        self.observation_space = spaces.Box(low=obersavtion_low, high=obersavtion_high)
        self.action_space = spaces.Discrete(n=len(ac_remote.Actions))

    def _next_observation(self):
        receive_new_data = False
        env_pack = dict()
        user_pack = dict()
        while (not receive_new_data):
            env_list = self.database.get(ENVIRONMENT_DATA_PATH)
            user_list = self.database.get(USER_DATA_PATH)
            if ((len(env_list)-1) % MAX_STEPS == self.current_step and (len(user_list)-1) % MAX_STEPS == self.current_step):
                env_pack = env_list.pop()
                user_pack = user_list.pop()
                receive_new_data = True

        obs = np.array([env_pack['temp'],env_pack['hum'], user_pack['body'], user_pack['type']])
        return obs

    def _take_action(self, action):
        _ , value = self.AC_remote.get_value_pair(action)
        self.action = value
        if (self.AC_remote.set_temperature is not value):
            command = self.AC_remote.get_action_command(temp=value)
            r.set("/Devices/"+AC_REMOTE_SERIAL_NUM,"receive_action",{"command":command, "is_new_action": True, "current_step": self.current_step})
        done_action = False
        while (not done_action):
            if (self.database.get(CHECK_FINISH_ACTION, is_dict=True)['is_new_action'] == False):
                done_action = True

    def step(self, action):
        self._take_action(action)

        feedback_pack = self.database.get(FEEDBACK_PATH).pop()
        feedback = "none"
        if (feedback_pack['stepNo'] == self.current_step):
            feedback = feedback_pack['feedback']

        delay_modifier = (self.current_step / MAX_STEPS)

        self.reward = feedback_mark(feedback) * delay_modifier

        self.current_step += 1

        if (self.current_step > MAX_STEPS):
            self.current_step = 0

        done = self.total_reward >= MAX_REWARD or self.current_step > MAX_STEPS

        obs = self._next_observation()

        return obs, self.reward, done, {}

    def reset(self):
        self.current_step = 0
        self.reward = 0
        self.total_reward = 0
        return self._next_observation()

    def render(self, mode="human", close=False):
        # Render the environment to the screen
        print(f'Step: {self.current_step}', end="|")
        print(f'Action: set to {self.action}', end="|")
        print(f'reward: {self.reward}', end="|")
        print(f'total_reward: {self.total_reward}')
