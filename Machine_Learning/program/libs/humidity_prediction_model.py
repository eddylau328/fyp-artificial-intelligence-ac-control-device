import json
import numpy as np
from enum import Enum
from time import time
from datetime import datetime
from tensorflow.python.keras.callbacks import TensorBoard
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LeakyReLU, Dropout
from tensorflow.keras import optimizers
from tensorflow.keras.utils import to_categorical
from sklearn.utils.class_weight import compute_class_weight
from matplotlib import pyplot

MAX_MIN_TABLE = {
    'outdoor_temp' : (22.254541, 2.3447716),
    'outdoor_hum' : (70.558945, 21.4994),
    'delta_time' : (76.91057, 33.42745),
    'time' : (37.865852, 13.623056)
}


##############################################################
#
#       Input layers              Range              Shape
#   -indoor temperature           17-30              (1,)
#   -indoor humidity              40-100             (1,)
#   -outdoor temperature          10-40              (1,)
#   -outdoor humidity             40-100             (1,)
#   -body temperature             28-35              (1,)
#   -AC temperature setting       17-25              (1,9)  <- need one hot encoding
#   -Fanspeed setting              1-3               (1,3)  <- need one hot encoding
#
##############################################################

def num_of_model():
    i = 1
    found = False
    while (not found):
        filepath = '../humidity_prediction_models/prediction_model_'+str(i)
        try:
            with open(filepath +'.h5', 'r') as file:
                i += 1
                # Do something with the file
        except IOError:
            found = True
            i -= 1
    return i

def num_of_paths():
    i = 1
    found = False
    while (not found):
        filepath = '../env_training_data/env_data_'+str(i)
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

class Env_Des(Enum):
    broken_clouds = 0
    light_intensity_shower_rain = 1
    mist = 2
    few_clouds = 3
    scattered_clouds = 4
    drizzle = 5
    clear_sky = 6
    overcast_clouds = 7
    light_rain = 8


# set_temp = 9
# set_fanspeed = 3

parameters = {
    'input_shape':18,
    'data_name':['temp','hum','outdoor_temp','outdoor_hum','outdoor_des','set_temp','set_fanspeed','time'],
    'output_shape': 1,
    'model_name': "Humidity Prediction"
}


class HumidityPredictionModel:

    def __init__(self, **kwargs):
        self.input_shape = kwargs['input_shape']
        self.output_shape = kwargs['output_shape']
        self.model_name = kwargs['model_name']
        self.data_name = kwargs['data_name']
        self.initiate_model()


    # initiate the keras model for supervised learning
    def initiate_model(self):
        self.model = Sequential(name=self.model_name)
        self.model.add(Dense(18, input_shape=(self.input_shape,), kernel_initializer='he_uniform',
                bias_initializer='zeros', activation='linear'))
        #self.model.add(LeakyReLU(alpha=0.01))
        #self.model.add(Dropout(0.1))

        self.model.add(Dense(self.output_shape, activation='linear'))
        optimizer = optimizers.Adam(lr=0.0002, decay=1e-6)
        self.tensorboard = TensorBoard(log_dir="logs/{}".format(time()))
        self.model.compile(loss="mean_squared_error", optimizer=optimizer, metrics=['mae'])


    def show_model(self):
        self.model.summary()


    def train(self):
        x , y = self.get_data()

        #print("x shape = {}".format(x.shape))
        #print("y shape = {}".format(y.shape))

        history = self.model.fit(x, y, batch_size=32, epochs=300, verbose=1, validation_split = 0.3, shuffle=True, callbacks=[self.tensorboard])
        pyplot.subplot(211)
        pyplot.title('Loss')
        pyplot.plot(history.history['loss'], label='train')
        pyplot.plot(history.history['val_loss'], label='test')
        pyplot.legend()

        pyplot.subplot(212)
        pyplot.title('MAE')
        pyplot.plot(history.history['mean_absolute_error'], label='train')
        pyplot.plot(history.history['val_mean_absolute_error'], label='test')
        pyplot.legend()
        pyplot.show()

        print("Save the trained model_name [Y/n]?  ", end="")
        decision = input()
        while(decision is not 'y' and decision is not 'Y' and decision is not 'n'):
            decision = input()

        if (decision == "y" or decision == "Y"):
            save_path = '../humidity_prediction_models/prediction_model_'+str(num_of_model()+1)+'.h5'
            self.model.save(save_path)


    def load_model(self, path):
        self.model = load_model(path)

    # predict the feedback the user will give
    def predict(self, inputs, delta_time, time):
        package = []
        # input should be a dictionary object
        for data in inputs:
            package_dict = {}
            for key in ['temp','hum','outdoor_temp','outdoor_hum','set_temp','set_fanspeed']:
                package_dict[key] = data[key]
            package.append(package_dict)

        pack = {
            'delta_temp'    : package[0]['temp'] - package[1]['temp'],
            'delta_hum'     : package[0]['hum'] - package[1]['hum'],
            'outdoor_temp'  : package[1]['outdoor_temp'],
            'outdoor_hum'   : package[1]['outdoor_hum'],
            'delta_time'    : delta_time,
            'time'          : time,
            'set_temp'      : package[1]['set_temp']-17,
            'set_fanspeed'  : package[1]['set_fanspeed']-1,
            }
        seperate_data = pack

        set_temp = np.array(seperate_data['set_temp']).reshape(-1)
        set_fanspeed = np.array(seperate_data['set_fanspeed']).reshape(-1)
        one_hot_set_temp = np.eye(9)[set_temp]
        one_hot_set_fanspeed = np.eye(3)[set_fanspeed]
        seperate_data['set_temp'] = one_hot_set_temp.reshape(-1).tolist()
        seperate_data['set_fanspeed'] = one_hot_set_fanspeed.reshape(-1).tolist()
        x = []
        for key in ['delta_temp','delta_hum','outdoor_temp','outdoor_hum','delta_time','time','set_temp','set_fanspeed']:
            if (key in ['set_temp','set_fanspeed']):
                for num in seperate_data[key]:
                    x.append(num)
            else:
                x.append(seperate_data[key])

        x = np.array(x).reshape((1,self.input_shape))
        x = self.normalize_data(x, MAX_MIN_TABLE)
        prediction = self.model.predict(x)
        return prediction.item() + package[1]['hum']


    def get_data(self):
        data = self.extract_data()
        data = self.process_data(data)
        x = []
        for dict_obj in data:
            x_data = []
            for key in ['delta_temp','delta_hum','outdoor_temp','outdoor_hum','delta_time','time','set_temp','set_fanspeed']:
                if (key in ['set_temp','set_fanspeed']):
                    for num in dict_obj[key]:
                        x_data.append(num)
                else:
                    x_data.append(dict_obj[key])
            x.append(x_data)

        y = []
        for dict_obj in data:
            y.append(dict_obj['output_hum'])
        # return as numpy array
        x = np.asarray(x, np.float32)
        # normalize data
        x = self.normalize_data(x)
        y = np.asarray(y, np.float32)
        #print(x)
        #print(y)
        return x, y


    def normalize_data(self, x, max_min_dict=None):
        x_field = ['delta_temp','delta_hum','outdoor_temp','outdoor_hum','delta_time','time','set_temp','set_fanspeed']
        for key in ['outdoor_temp','outdoor_hum','delta_time','time']:
            col_index = x_field.index(key)
            if (max_min_dict == None):
                mean, std = np.mean(x[:, col_index]), np.std(x[:, col_index])
            else:
                mean, std = max_min_dict[key][0], max_min_dict[key][1]
            #print("{} (mean, std) = {}".format(key,(mean, std)))
            x[:, col_index] = (x[:, col_index]-mean)/(std)
            #print(x)
        return x


    # extract data from the env_training_data folder
    def extract_data(self):
        datapack = []
        for i in range(1, num_of_paths()+1):
            datapack.append(get_data('../env_training_data/env_data_'+str(i)+'.json', 'datapack'))
        extract_data = []
        for pack in datapack:
            packs = []
            for dict_obj in pack:
                value = {}
                for key in self.data_name:
                    value[key] = dict_obj[key]
                packs.append(value)
            extract_data.append(packs)
        return extract_data


    def process_data(self, data):
        # extract feedback and change to Enum name first
        seperate_data = []
        for package in data:
            isFinish = False
            count = 0
            while(not isFinish):
                if (count <= len(package)-3):
                    str_pre_time, str_mid_time, str_curr_time = package[count]['time'], package[count+1]['time'], package[count+2]['time']
                    pre_time = datetime.strptime(str_pre_time, '%Y-%m-%d %H:%M:%S.%f')
                    mid_time = datetime.strptime(str_mid_time, '%Y-%m-%d %H:%M:%S.%f')
                    curr_time = datetime.strptime(str_curr_time, '%Y-%m-%d %H:%M:%S.%f')
                    pack = {
                        'delta_temp'    : package[count]['temp'] - package[count+1]['temp'],
                        'delta_hum'     : package[count]['hum'] - package[count+1]['hum'],
                        'output_temp'   : package[count+1]['temp'] - package[count+2]['temp'],
                        'output_hum'    : package[count+1]['hum'] - package[count+2]['hum'],
                        'outdoor_temp'  : package[count+1]['outdoor_temp'],
                        'outdoor_hum'   : package[count+1]['outdoor_hum'],
                        'delta_time'    : (curr_time-pre_time).seconds,
                        'time'          : (mid_time-pre_time).seconds,
                        'set_temp'      : package[count+1]['set_temp']-17,
                        'set_fanspeed'  : package[count+1]['set_fanspeed']-1,
                    }
                    seperate_data.append(pack)
                    count += 3
                else:
                    isFinish = True

        for encode_name in ['set_temp','set_fanspeed']:
            field_data = []
            for dict_obj in seperate_data:
                field_data.append(dict_obj[encode_name])
            field_data = self.one_hot_encoder(field_data).tolist()
            i = 0
            for one_hot in field_data:
                seperate_data[i][encode_name] = one_hot
                i += 1

        return seperate_data


    def one_hot_encoder(self, data):
        data = np.array(data)
        encoded = to_categorical(data)
        return encoded


def create_model():
    return HumidityPredictionModel(**parameters)


if (__name__ == '__main__'):
    model = create_model()
    model.show_model()
    model.train()
'''
    model.load_model(path="../humidity_prediction_models/prediction_model_1.h5")
    inputs = [{
           "body": 32.59375,
           "feedback": "acceptable",
           "hum": 63.799999237,
           "light": 29.166671753,
           "move_type": "work",
           "outdoor_des": "few clouds",
           "outdoor_hum": 69,
           "outdoor_press": 101.7,
           "outdoor_temp": 23.410000000000025,
           "press": 101.700004578,
           "set_fanspeed": 1,
           "set_temp": 22,
           "stepNo": 28,
           "temp": 23.899999619,
           "time": "2020-04-26 22:13:22.965329"
          },
          {
           "body": 32.5625,
           "feedback": "acceptable",
           "hum": 68.099998474,
           "light": 29.166671753,
           "move_type": "work",
           "outdoor_des": "few clouds",
           "outdoor_hum": 69,
           "outdoor_press": 101.7,
           "outdoor_temp": 23.420000000000016,
           "press": 101.700004578,
           "set_fanspeed": 1,
           "set_temp": 22,
           "stepNo": 29,
           "temp": 23.899999619,
           "time": "2020-04-26 22:14:00.620303"
          }]
    test = {
           "body": 32.5,
           "feedback": "acceptable",
           "hum": 70.900001526,
           "light": 29.166671753,
           "move_type": "work",
           "outdoor_des": "few clouds",
           "outdoor_hum": 69,
           "outdoor_press": 101.7,
           "outdoor_temp": 23.410000000000025,
           "press": 101.700004578,
           "set_fanspeed": 1,
           "set_temp": 24,
           "stepNo": 30,
           "temp": 23.899999619,
           "time": "2020-04-26 22:14:37.543160"
          }

    str_pre_time, str_curr_time = inputs[0]['time'], test['time']
    pre_time = datetime.strptime(str_pre_time, '%Y-%m-%d %H:%M:%S.%f')
    curr_time = datetime.strptime(str_curr_time, '%Y-%m-%d %H:%M:%S.%f')
    delta_time = (curr_time-pre_time).seconds
    print(model.predict(inputs, delta_time), test['hum'])

'''
