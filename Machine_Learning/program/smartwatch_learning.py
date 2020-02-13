import json
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv1D, MaxPool1D



def get_data(path, dataname):
    with open(path, 'r') as file:
        json_file = json.load(file)
    return json_file[dataname]


dict_list = get_data("smartwatch_data/work_acc.json", "acc")
data = [[dict_obj["acc_x"], dict_obj["acc_y"], dict_obj["acc_z"]] for dict_obj in dict_list]


#model = Sequential()
#model.add(Conv1D(30, 3, activation='relu', input_shape=(,)))
