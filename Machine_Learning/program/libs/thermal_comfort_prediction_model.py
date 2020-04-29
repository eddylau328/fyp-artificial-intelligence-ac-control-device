import json
import numpy as np
from enum import Enum
from time import time
from tensorflow.python.keras.callbacks import TensorBoard
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LeakyReLU, Dropout
from tensorflow.keras import optimizers
from tensorflow.keras.utils import to_categorical
from sklearn.utils.class_weight import compute_class_weight
from matplotlib import pyplot

MAX_MIN_TABLE = {
    'temp' : (28.6, 19.0),
    'hum' : (87.8, 39.5),
    'outdoor_temp' : (27.67, 19.0),
    'outdoor_hum' : (100.0, 26.0),
    'body' : (34.75, 29.4375)
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
        filepath = '../thermal_comfort_predict_models/prediction_model_'+str(i)
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


class Feedback(Enum):
    very_hot = 0
    hot = 1
    a_bit_hot = 2
    comfy = 3
    a_bit_cold = 4
    cold = 5
    very_cold = 6


class Move(Enum):
    work = 0
    rest = 1
    sleep = 2


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
    'input_shape':5,
    'data_name':['temp','hum','outdoor_temp','outdoor_hum','body','move_type','outdoor_des','set_temp','set_fanspeed','feedback'],
    'one_hot_encode_required':['move_type','outdoor_des','set_temp','set_fanspeed','feedback'],
    'x':['temp','hum','outdoor_temp','outdoor_hum','body'],
    'y':['feedback'],
    'normalize':['temp','hum','outdoor_temp','outdoor_hum','body'],
    'output_shape': len(Feedback),
    'feedback_amplifier': 5,
    'replace_acceptable': True,
    'model_name': "Thermal Comfort Prediction Model"
}


class Thermal_Comfort_Predict_Model:

    def __init__(self, **kwargs):
        self.input_shape = kwargs['input_shape']
        self.output_shape = kwargs['output_shape']
        self.model_name = kwargs['model_name']
        self.data_name = kwargs['data_name']
        self.one_hot_encode_name = kwargs['one_hot_encode_required']
        self.feedback_amplifier = kwargs['feedback_amplifier']
        self.replace_acceptable = kwargs['replace_acceptable']
        self.normalize_data_name = kwargs['normalize']
        self.x_field = kwargs['x']
        self.y_field = kwargs['y']
        self.initiate_model()


    # initiate the keras model for supervised learning
    def initiate_model(self):
        self.model = Sequential(name=self.model_name)
        self.model.add(Dense(48, input_shape=(self.input_shape,), kernel_initializer='random_uniform',
                bias_initializer='zeros', activation='linear'))
        self.model.add(LeakyReLU(alpha=0.01))
        self.model.add(Dropout(0.2))
        self.model.add(Dense(128, input_shape=(self.input_shape,), kernel_initializer='random_uniform',
                bias_initializer='zeros', activation='linear'))
        self.model.add(LeakyReLU(alpha=0.05))
        self.model.add(Dropout(0.1))
        self.model.add(Dense(128, input_shape=(self.input_shape,), kernel_initializer='random_uniform',
                bias_initializer='zeros', activation='linear'))
        self.model.add(LeakyReLU(alpha=0.05))
        self.model.add(Dropout(0.1))
        self.model.add(Dense(48, kernel_initializer='random_uniform',
                bias_initializer='zeros',  activation='linear'))
        self.model.add(LeakyReLU(alpha=0.01))
        self.model.add(Dropout(0.2))

        self.model.add(Dense(self.output_shape, activation='softmax'))
        optimizer = optimizers.Adam(lr=0.0004, decay=1e-6)
        self.tensorboard = TensorBoard(log_dir="logs/{}".format(time()))
        self.model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=['accuracy'])


    def show_model(self):
        self.model.summary()


    def train(self):
        x , y = self.get_data()

        #print("x shape = {}".format(x.shape))
        #print("y shape = {}".format(y.shape))
        for i in range(self.output_shape):
            print('{:<10} has {} data.'.format(Feedback(i).name,len(np.where(y[:,i] == 1)[0])))
        print("_________________________________________________________________")
        print('{:<10} has {} data'.format("Total",y.shape[0]))

        history = self.model.fit(x, y, batch_size=32, epochs=100, verbose=1, validation_split = 0.2, shuffle=True, callbacks=[self.tensorboard])
        pyplot.subplot(211)
        pyplot.title('Loss')
        pyplot.plot(history.history['loss'], label='train')
        pyplot.plot(history.history['val_loss'], label='test')
        pyplot.legend()
        # plot accuracy during training
        pyplot.subplot(212)
        pyplot.title('Accuracy')
        pyplot.plot(history.history['acc'], label='train')
        pyplot.plot(history.history['val_acc'], label='test')
        pyplot.legend()
        pyplot.show()

        print("Save the trained model_name [Y/n]?  ", end="")
        decision = input()
        while(decision is not 'y' and decision is not 'Y' and decision is not 'n'):
            decision = input()

        if (decision == "y" or decision == "Y"):
            save_path = '../thermal_comfort_predict_models/prediction_model_'+str(num_of_model()+1)+'.h5'
            self.model.save(save_path)


    def load_model(self, path):
        self.model = load_model(path)

    # predict the feedback the user will give
    def predict(self, input):
        x_list = []
        # input should be a dictionary object
        for key in self.x_field:
            x_list.append(input[key])
        X = np.array(x_list).reshape((1,len(self.x_field)))
        X = self.normalize_data(X,MAX_MIN_TABLE)
        predict_feedback = self.model.predict(X)
        prediction = np.around((predict_feedback*100),decimals=1)
        '''
        print()
        print("Current Environment Reading")
        print("Temperature          = {:0.2f}".format(input['temp']))
        print("Humidity             = {:0.2f}".format(input['hum']))
        print("Outdoor Temperature  = {:0.2f}".format(input['outdoor_temp']))
        print("Outdoor Humidity     = {:0.2f}".format(input['outdoor_hum']))
        print("Skin Temperature     = {:0.2f}".format(input['body']))
        print()
        '''
        feedback = Feedback(np.argmax(prediction)).name
        return feedback


    def get_data(self):
        data = self.extract_data()
        data = self.amplify_feedback(data)
        data = self.process_data(data)
        x = []
        for dict_obj in data:
            x_data = []
            for key in self.x_field:
                if (key in self.one_hot_encode_name):
                    for num in dict_obj[key]:
                        x_data.append(num)
                else:
                    x_data.append(dict_obj[key])
            x.append(x_data)

        y = []
        for dict_obj in data:
            y_data = []
            for key in self.y_field:
                if (key in self.one_hot_encode_name):
                    for num in dict_obj[key]:
                        y_data.append(num)
                else:
                    y_data.append(dict_obj[key])
            y.append(y_data)
        # return as numpy array
        x = np.asarray(x, np.float32)
        # normalize data
        x = self.normalize_data(x)
        y = np.asarray(y, np.float32)
        #print(x)
        #print(y)
        return x, y


    def normalize_data(self, x, max_min_dict=None):
        for key in self.normalize_data_name:
            col_index = self.x_field.index(key)
            if (max_min_dict == None):
                max, min = x[:, col_index].max(), x[:, col_index].min()
            else:
                max, min = max_min_dict[key][0], max_min_dict[key][1]
            #print("{} (max,min) = {}".format(key,(max, min)))
            x[:, col_index] = (x[:, col_index]-min)/(max-min)
        return x



    # decreasing the acceptable feedback
    def amplify_feedback(self, data):
        feedback = []
        for dict_obj in data:
            feedback.append(dict_obj['feedback'])

        if (self.replace_acceptable is True):
            i = 0
            while(i < len(feedback)-1):
                if (feedback[i] != "acceptable"):
                    break
                i += 1
            for j in range(0, i):
                feedback[j] = feedback[i]

            while(i < (len(feedback)-1)):
                if (feedback[i] != "acceptable"):
                    j = i + 1
                    while (True):
                        if (j > len(feedback)-1):
                            i = j
                            break
                        if (feedback[j] == "acceptable"):
                            feedback[j] = feedback[i]
                        else:
                            i = j - 1
                            #feedback[i-1] = feedback[i]
                            break
                        j += 1
                i += 1
            i = 0
            for dict_obj in data:
                dict_obj['feedback'] = feedback[i]
                i += 1
            #skip_data = [j for j in range(1,len(data),2)]
            #skip_data.reverse()
            #for index in skip_data:
            #    data.pop(index)

        else:
            i = 0
            while(i < (len(feedback)-1)):
                if (feedback[i] != "acceptable"):
                    for j in range(1, (self.feedback_amplifier+1)*2):
                        if (i+j > len(feedback)-1):
                            i = i+j
                            break
                        if (feedback[i+j] == "acceptable" and j%2 == 1):
                            feedback[i+j] = feedback[i]
                        else:
                            i = i+j
                            break
                i += 1

            delete_acceptable = []
            for i in range(0, len(feedback)):
                if (feedback[i] == "acceptable"):
                    delete_acceptable.append(i)

            i = 0
            for dict_obj in data:
                dict_obj['feedback'] = feedback[i]
                i+=1

            delete_acceptable.reverse()

            for index in delete_acceptable:
                data.pop(index)
            for dict_obj in data:
                print(dict_obj['feedback'])
        return data

    # extract data from the env_training_data folder
    def extract_data(self):
        datapack = []
        for i in range(1, num_of_paths()+1):
            datapack.append(get_data('../env_training_data/env_data_'+str(i)+'.json', 'datapack'))
        data = []
        for pack in datapack:
            for dict_obj in pack:
                data.append(dict_obj)

        extract_data = []
        for pack in data:
            value = {}
            for key in self.data_name:
                value[key] = pack[key]
            extract_data.append(value)

        return extract_data


    def process_data(self, data):
        # extract feedback and change to Enum name first
        feedback = []
        move = []
        outdoor_des = []
        previous_move = ""

        for dict_obj in data:
            dict_obj['set_temp'] -= 17
            dict_obj['set_fanspeed'] -= 1
            str_move = dict_obj['move_type']
            if (str_move == ""):
                str_move = previous_move
            previous_move = str_move
            move.append(Move[str_move].value)
            str_env_des = dict_obj['outdoor_des']
            str_env_des = str_env_des.lower()
            str_env_des = str_env_des.replace(' ', '_')
            outdoor_des.append(Env_Des[str_env_des].value)
            str_feedback = dict_obj['feedback']
            str_feedback = str_feedback.lower()
            str_feedback = str_feedback.replace(' ', '_')

            #if (str_feedback == "very_cold"):
            #    str_feedback = "cold"
            #if (str_feedback == "very_hot" or str_feedback == "hot" or str_feedback == "a_bit_hot"):
            #    str_feedback = "hot"

            # change feedback name to number
            feedback.append(Feedback[str_feedback].value)

        i = 0
        for num in feedback:
            data[i]['feedback'] = num
            i += 1

        i = 0
        for num in move:
            data[i]['move_type'] = num
            i += 1

        i = 0
        for num in outdoor_des:
            data[i]['outdoor_des'] = num
            i += 1

        for encode_name in self.one_hot_encode_name:
            field_data = []
            for dict_obj in data:
                field_data.append(dict_obj[encode_name])
            field_data = self.one_hot_encoder(field_data).tolist()
            i = 0
            for one_hot in field_data:
                data[i][encode_name] = one_hot
                i += 1

        return data


    def one_hot_encoder(self, data):
        data = np.array(data)
        encoded = to_categorical(data)
        return encoded


def create_model():
    return Thermal_Comfort_Predict_Model(**parameters)


if (__name__ == '__main__'):
    model = create_model()
    model.show_model()
    #model.train()
    model.load_model(path="../thermal_comfort_predict_models/prediction_model_1.h5")
    pkg =  {
           "body": 31.0625,
           "feedback": "Cold",
           "hum": 48.600002289,
           "light": 29.166671753,
           "move_type": "work",
           "outdoor_des": "broken clouds",
           "outdoor_hum": 30,
           "outdoor_press": 101.8,
           "outdoor_temp": 20.879999999999995,
           "press": 101.800003052,
           "set_fanspeed": 1,
           "set_temp": 18,
           "stepNo": 124,
           "temp": 21.899999619,
           "time": "2020-04-13 18:37:45.586257"
          }
    print(model.predict(pkg))
