import json
import numpy as np
from enum import Enum
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical

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
    acceptable = 4
    a_bit_cold = 5
    cold = 6
    very_cold = 7


parameters = {
    'input_shape':17,
    'data_name':['temp','hum','outdoor_temp','outdoor_hum','body','set_temp','set_fanspeed','feedback'],
    'one_hot_encode_required':['set_temp','set_fanspeed','feedback'],
    'x':['temp','hum','outdoor_temp','outdoor_temp','body','set_temp','set_fanspeed'],
    'y':['feedback'],
    'output_shape': 8,
    'feedback_amplifier': 4,
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
        self.x_field = kwargs['x']
        self.y_field = kwargs['y']
        self.initiate_model()


    # initiate the keras model for supervised learning
    def initiate_model(self):
        self.model = Sequential(name=self.model_name)
        self.model.add(Dense(64, input_shape=(self.input_shape,), activation='relu'))
        self.model.add(Dense(520, activation='relu'))
        self.model.add(Dense(1024, activation='relu'))
        self.model.add(Dense(1024, activation='relu'))
        self.model.add(Dense(520, activation='relu'))
        self.model.add(Dense(self.output_shape, activation='softmax'))
        self.model.compile(loss="categorical_crossentropy", optimizer='adam', metrics=['accuracy'])
        self.model.summary()


    def train(self):
        x , y = self.get_data()
        print(x.shape)
        print(y.shape)
        self.model.fit(x, y, batch_size=32, validation_split = 0.1)


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
        return np.asarray(x, np.float32), np.asarray(y, np.float32)


    # decreasing the acceptable feedback
    def amplify_feedback(self, data):
        feedback = []
        for dict_obj in data:
            feedback.append(dict_obj['feedback'])
        i = 0
        while(i < (len(feedback)-1)):
            if (feedback[i] != "acceptable"):
                for j in range(1, self.feedback_amplifier+1):
                    if (i+j > len(feedback)-1):
                        i = i+j
                        break
                    if (feedback[i+j] == "acceptable"):
                        feedback[i+j] = feedback[i]
                    else:
                        i = i+j
                        break
            i += 1

        i = 0
        for dict_obj in data:
            dict_obj['feedback'] = feedback[i]
            i += 1
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
        for dict_obj in data:
            dict_obj['set_temp'] -= 17
            dict_obj['set_fanspeed'] -= 1
            str_feedback = dict_obj['feedback']
            str_feedback = str_feedback.lower()
            str_feedback = str_feedback.replace(' ', '_')
            # change feedback name to number
            feedback.append(Feedback[str_feedback].value)

        i = 0
        for num in feedback:
            data[i]['feedback'] = num
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


if (__name__ == '__main__'):
    model = SupervisedLearning(**parameters)
    model.train()
