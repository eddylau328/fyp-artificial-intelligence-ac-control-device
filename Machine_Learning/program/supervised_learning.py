import json
import numpy as np
from enum import Enum
from time import time
from libs import ac_firebase_remote as ac_remote
from tensorflow.python.keras.callbacks import TensorBoard
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LeakyReLU, Dropout
from tensorflow.keras import optimizers
from tensorflow.keras.utils import to_categorical
from sklearn.utils.class_weight import compute_class_weight
from matplotlib import pyplot as plt

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
        filepath = 'trained_models_output_7/prediction_model_'+str(i)
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

'''
class Feedback(Enum):
    hot = 0
    comfy = 1
    a_bit_cold = 2
    cold = 3
'''

# set_temp = 9
# set_fanspeed = 3

parameters = {
    'input_shape':17,
    'data_name':['temp','hum','outdoor_temp','outdoor_hum','body','move_type','outdoor_des','set_temp','set_fanspeed','feedback'],
    'one_hot_encode_required':['move_type','outdoor_des','set_temp','set_fanspeed','feedback'],
    'x':['temp','hum','outdoor_temp','outdoor_hum','body','set_temp','set_fanspeed'],
    'y':['feedback'],
    'normalize':['temp','hum','outdoor_temp','outdoor_hum','body'],
    'output_shape': len(Feedback),
    'feedback_amplifier': 7,
    'replace_acceptable': True,
    'model_name': "Supervised Learning"
}


class SupervisedLearning:

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
        self.model.add(Dense(128, input_shape=(self.input_shape,), kernel_initializer='random_uniform',
                bias_initializer='zeros', activation='linear'))
        self.model.add(LeakyReLU(alpha=0.1))
        #self.model.add(Dropout(0.2))

        self.model.add(Dense(512, kernel_initializer='random_uniform',
                bias_initializer='zeros',  activation='linear'))
        self.model.add(LeakyReLU(alpha=0.05))
        #self.model.add(Dropout(0.2))

        self.model.add(Dense(128, kernel_initializer='random_uniform',
                bias_initializer='zeros',  activation='linear'))
        self.model.add(LeakyReLU(alpha=0.05))
        #self.model.add(Dropout(0.2))

        self.model.add(Dense(self.output_shape, activation='softmax'))
        optimizer = optimizers.Adam(lr=0.00003, decay=1e-6)
        self.tensorboard = TensorBoard(log_dir="logs/{}".format(time()))
        self.model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=['accuracy'])
        self.model.summary()


    def train(self):
        x , y = self.get_data()

        #print("x shape = {}".format(x.shape))
        #print("y shape = {}".format(y.shape))
        for i in range(self.output_shape):
            print('{:<10} has {} data.'.format(Feedback(i).name,len(np.where(y[:,i] == 1)[0])))
        print("_________________________________________________________________")
        print('{:<10} has {} data'.format("Total",y.shape[0]))

        history = self.model.fit(x, y, batch_size=24, epochs=150, verbose=1, validation_split = 0.2, shuffle=True, callbacks=[self.tensorboard])


        fig = plt.figure()
        fig.subplots_adjust(hspace=.5)
        ax1 = fig.add_subplot(2,1,1)
        ax1.set_title('Categorical Crossentropy Loss per Epoch')
        ax1.set_ylabel('Loss')
        ax1.set_xlabel('Epoch')
        ax1.plot(history.history['loss'], label='train')
        ax1.plot(history.history['val_loss'], label='test')
        ax1.legend()
        # plot accuracy during training
        ax2 = fig.add_subplot(2,1,2)
        ax2.set_title('Accuracy per Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.plot(history.history['acc'], label='train')
        ax2.plot(history.history['val_acc'], label='test')
        ax2.legend()
        plt.show()

        print("Save the trained model_name [Y/n]?  ", end="")
        decision = input()
        while(decision is not 'y' and decision is not 'Y' and decision is not 'n'):
            decision = input()

        if (decision == "y" or decision == "Y"):
            save_path = 'trained_models_output_7/prediction_model_'+str(num_of_model()+1)+'.h5'
            self.model.save(save_path)


    def load_model(self, model_name=None):
        if (model_name == None):
            save_path = 'trained_models_output_7/prediction_model_'+str(num_of_model())+'.h5'
        else:
            save_path = model_name
        self.model = load_model(save_path)

    # predict the feedback the user will give
    def predict(self, input, control_pairs = None):
        x_list = []
        # input should be a dictionary object
        for key in self.x_field:
            if (key in input and key != "set_temp" and key != "set_fanspeed"):
                x_list.append(input[key])
        if (control_pairs == None):
            size = len(ac_remote.Actions_Temp)*len(ac_remote.Actions_Fanspeed)
            X = np.zeros((size,self.input_shape))
            X[:,0:len(x_list)]= np.asarray(x_list, np.float32)
            temp_action_list, fan_action_list = [], []
            action_combination = np.zeros((size,len(ac_remote.Actions_Temp)+len(ac_remote.Actions_Fanspeed)))
            for temp_action in ac_remote.Actions_Temp:
                for fan_action in ac_remote.Actions_Fanspeed:
                    temp_action_list.append(temp_action.value)
                    fan_action_list.append(fan_action.value)
            action_pair = np.zeros((size,2))
            action_pair[:,0] = np.asarray(temp_action_list)
            action_pair[:,1] = np.asarray(fan_action_list)
            temp_action_list = self.one_hot_encoder(temp_action_list)
            fan_action_list = self.one_hot_encoder(fan_action_list)
            action_combination[:, 0:len(ac_remote.Actions_Temp)] = temp_action_list
            action_combination[:, len(ac_remote.Actions_Temp):len(ac_remote.Actions_Temp)+len(ac_remote.Actions_Fanspeed)] = fan_action_list
            X[:,len(x_list):] = action_combination[:,:]
            X = self.normalize_data(X,MAX_MIN_TABLE)
            #print(X)
            predict_feedback = self.model.predict(X)
            '''
            prediction = np.around((predict_feedback*100),decimals=1)
            print()
            print("Current Environment Reading")
            print("Temperature          = {:0.2f}".format(input['temp']))
            print("Humidity             = {:0.2f}".format(input['hum']))
            print("Outdoor Temperature  = {:0.2f}".format(input['outdoor_temp']))
            print("Outdoor Humidity     = {:0.2f}".format(input['outdoor_hum']))
            print("Skin Temperature     = {:0.2f}".format(input['body']))
            print()
            for i in range(size):
                print('(Temp, fanspeed) {} probability get {:0.2f}%'.format(((action_pair[i,0]+17,action_pair[i,1]+1)), prediction[i,1]))
            '''
            comfy_feedback = predict_feedback[:, 3]
            #print(predict_feedback)
            translated_feedback = np.argmax(predict_feedback, axis=1)
            sorted_index = (-comfy_feedback).argsort()
            sorted_comfy_feedback = comfy_feedback[sorted_index]
            sorted_action_pair = action_pair[sorted_index]
            return sorted_action_pair.tolist(), sorted_comfy_feedback.tolist()
        else:
            # input should be a dictionary object
            X = np.zeros((1,17))
            control_pairs[0], control_pairs[1] = int(control_pairs[0]-17), int(control_pairs[1]-1)
            one_hot_set_temp = np.eye(9)[control_pairs[0]]
            one_hot_set_fanspeed = np.eye(3)[control_pairs[1]]
            X[:,0:len(x_list)] = np.array(x_list)
            X[:,len(x_list):len(x_list)+9] = one_hot_set_temp
            X[:,len(x_list)+9:len(x_list)+9+3] = one_hot_set_fanspeed
            X = self.normalize_data(X,MAX_MIN_TABLE)
            predict_feedback = self.model.predict(X)
            return predict_feedback[:, 3]


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
            datapack.append(get_data('env_training_data/env_data_'+str(i)+'.json', 'datapack'))
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
        '''
        record = []
        i = 0
        for dict_obj in data:
            if (dict_obj['feedback'] == "Very Hot" or dict_obj['feedback'] == "Hot" or dict_obj['feedback'] == "A Bit Hot"):
                record.append(i)
            i += 1

        record.reverse()

        for index in record:
            data.pop(index)
        '''

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
    return SupervisedLearning(**parameters)


if (__name__ == '__main__'):
    model = SupervisedLearning(**parameters)

    model.train()
    inputs = [  {
       "body": 33.3125,
       "feedback": "acceptable",
       "hum": 74,
       "light": 26.666671753,
       "move_type": "work",
       "outdoor_des": "scattered clouds",
       "outdoor_hum": 88,
       "outdoor_press": 101.6,
       "outdoor_temp": 20.25,
       "press": 101.5,
       "set_fanspeed": 1,
       "set_temp": 24,
       "stepNo": 86,
       "temp": 21.700000763,
       "time": "2020-04-23 00:02:45.125860"
      },
      {
       "body": 33.3125,
       "feedback": "acceptable",
       "hum": 75.200004578,
       "light": 26.666671753,
       "move_type": "work",
       "outdoor_des": "scattered clouds",
       "outdoor_hum": 88,
       "outdoor_press": 101.6,
       "outdoor_temp": 20.260000000000048,
       "press": 101.5,
       "set_fanspeed": 1,
       "set_temp": 24,
       "stepNo": 87,
       "temp": 21.899999619,
       "time": "2020-04-23 00:03:20.983475"
      },
      {
       "body": 33.3125,
       "feedback": "acceptable",
       "hum": 77,
       "light": 26.666671753,
       "move_type": "work",
       "outdoor_des": "scattered clouds",
       "outdoor_hum": 88,
       "outdoor_press": 101.6,
       "outdoor_temp": 20.25,
       "press": 101.5,
       "set_fanspeed": 1,
       "set_temp": 24,
       "stepNo": 88,
       "temp": 22.100000381,
       "time": "2020-04-23 00:03:57.864873"
      },
      {
       "body": 33.333332062,
       "feedback": "acceptable",
       "hum": 77.800003052,
       "light": 26.666671753,
       "move_type": "work",
       "outdoor_des": "scattered clouds",
       "outdoor_hum": 88,
       "outdoor_press": 101.6,
       "outdoor_temp": 20.25,
       "press": 101.5,
       "set_fanspeed": 1,
       "set_temp": 24,
       "stepNo": 89,
       "temp": 22.200000763,
       "time": "2020-04-23 00:04:34.403887"
      }]

    '''
    model.load_model()
    i = 1
    for data in inputs:
        print(i)
        i+= 1
        pairs, prob_comfy = model.predict(data)
        pairs, prob_comfy = np.array(pairs), np.array(prob_comfy)*100
        pairs[:, 0] = pairs[:, 0] + 17
        pairs[:, 1] = pairs[:, 1] + 1
        display = np.zeros((27,3))
        display[:,0:2] = pairs
        display[:,2] = prob_comfy
        print(display[0:5,:])
    '''
