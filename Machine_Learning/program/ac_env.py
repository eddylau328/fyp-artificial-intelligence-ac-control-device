import gym
import numpy as np
import enum
from libs import realtime_firebase as rt
from gym import spaces

MAX_REWARD = 100
ENVIRONMENT_DATA_PATH = "Devices/fyp0001/sensors"
USER_DATA_PATH = "Devices/watch0001/datapack"

class Actions(enum.Enum):
    Temp_25 = 0
    Temp_24 = 1
    Temp_23 = 2
    Temp_22 = 3
    Temp_21 = 4
    Temp_20 = 5
    Temp_19 = 6
    Temp_18 = 7


class AC_Env(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes' : ['human']}

    def __init__(self):
        super(AC_Env, self).__init__()

        self.df = None
        self.database = rt.Realtime_firebase()
        self.reward_range = (0, MAX_REWARD)

        #temperature, humidity, body temperature, type_of_move
        obersavtion_high = np.array([40.0, 100.0, 40, 3])
        obersavtion_low = np.array([15.0, 0.0, 25, 1])
        self.observation_space = spaces.box(low=obersavtion_low, high=obersavtion_high)
        self.action_space = spaces.Discrete(n=len(Actions))

    def _next_observation(self):
        env_pack = self.database.get(ENVIRONMENT_DATA_PATH).pop()
        user_pack = self.database.get(USER_DATA_PATH).pop()
        obs = np.array([env_pack['temp'],env_pack['hum'], user_pack['body'], user_pack['type']])
        return obs

    #def _take_action(self, action):

