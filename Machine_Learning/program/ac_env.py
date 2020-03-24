import gym
import enum
import numpy as np
from libs import realtime_firebase as rt
from libs import ac_firebase_remote as ac_remote
from gym import spaces

MAX_REWARD = 100
ENVIRONMENT_DATA_PATH = "Devices/fyp0001/sensors"
USER_DATA_PATH = "Devices/watch0001/datapack"
AC_REMOTE_SERIAL_NUM = "fyp0001"


class FeedBack(enum.Enum):
    hot = 0
    a_bit_hot = 1
    comfy = 2
    a_bit_cold = 3
    cold = 4


class AC_Env(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes' : ['human']}

    def __init__(self):
        super(AC_Env, self).__init__()

        self.df = None
        self.database = rt.Realtime_firebase()
        self.ac_remote = AC_remote(AC_REMOTE_SERIAL_NUM)
        self.reward_range = (0, MAX_REWARD)
        #temperature, humidity, body temperature, type_of_move
        obersavtion_high = np.array([40.0, 100.0, 40, 3])
        obersavtion_low = np.array([15.0, 0.0, 25, 1])
        self.observation_space = spaces.box(low=obersavtion_low, high=obersavtion_high)
        self.action_space = spaces.Discrete(n=len(ac_remote.Actions))

    def _next_observation(self):
        env_pack = self.database.get(ENVIRONMENT_DATA_PATH).pop()
        user_pack = self.database.get(USER_DATA_PATH).pop()
        obs = np.array([env_pack['temp'],env_pack['hum'], user_pack['body'], user_pack['type']])
        return obs

    def _take_action(self, action):
        _ , value = self.AC_remote.get_value_pair(action)
        command = self.AC_remote.get_action_command(temp=value)
        r.set("/Devices/"+AC_REMOTE_SERIAL_NUM,"receive_action",{"command":command, "is_new_action": True, "current_step": self.current_step})

    def step(self, action):
        self._take_action(action)

        self.current_step += 1


        obs = self._next_observation()

        return obs, reward, done, {}
