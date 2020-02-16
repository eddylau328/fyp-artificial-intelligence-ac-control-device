import json
from random import shuffle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv1D, MaxPooling1D



def get_data(path, dataname):
    with open(path, 'r') as file:
        json_file = json.load(file)
    return json_file[dataname]


def process_data(data):
    data_list = []
    for obj in data:
        for dict_obj in obj:
            data_list.append(dict_obj)
    return data_list


def copy_list(dict_list, size, overlap_size):
    iterate = 1
    acc_x, acc_y, acc_z = [], [], []
    x = []
    for j in range(len(dict_list)):
        dict_obj = dict_list[j]
        acc_x.append(dict_obj['acc_x'])
        acc_y.append(dict_obj['acc_y'])
        acc_z.append(dict_obj['acc_z'])
        if (iterate == overlap_size):
            x = copy_list(dict_list[j+1:], size, overlap_size)
        if (iterate == size):
            if x is not []:
                x.append([acc_x,acc_y,acc_z])
            else:
                x = [[acc_x,acc_y,acc_z],]
            return x

        iterate += 1

    return x


def transform_2_train_data(dict_list, size, y_value, x_train, y_train, overlap=False, overlap_size=1):
    if (overlap == False):
        overlap_size = size
    x = copy_list(dict_list, size, overlap_size)
    y = [y_value for i in range(len(x))]

    for data in x:
        x_train.append(data)
    for data in y:
        y_train.append(data)

    return x_train, y_train

SLEEP_DATA_SIZE = 2
REST_DATA_SIZE = 2
#move_acc = get_data("smartwatch_data/move_acc.json", "acc")
#move_acc = process_data(move_acc)

work_acc = get_data("smartwatch_data/work_acc_4hz.json", "acc")
work_acc = process_data(work_acc)

sleep_acc = []
for i in range(SLEEP_DATA_SIZE):
    sleep_acc.append(process_data(get_data("smartwatch_data/sleep_acc_4hz_"+str(i)+".json", "acc")))

rest_acc = []
for i in range(SLEEP_DATA_SIZE):
    rest_acc.append(process_data(get_data("smartwatch_data/rest_acc_4hz_"+str(i)+".json", "acc")))

x_train, y_train = [], []
x_train, y_train = transform_2_train_data(work_acc, 40, 0, x_train, y_train, overlap=True, overlap_size=40)
print("Size of work_acc data is %s" %len(x_train))
tmp = len(x_train)



for i in range(SLEEP_DATA_SIZE):
    x_train, y_train = transform_2_train_data(sleep_acc[i], 40, 1, x_train, y_train, overlap=True, overlap_size=40)
    print("Size of sleep_acc data "+str(i) + " is %s" %(len(x_train)-tmp))
    tmp = len(x_train)

for i in range(REST_DATA_SIZE):
    x_train, y_train = transform_2_train_data(rest_acc[i], 40, 2, x_train, y_train, overlap=True, overlap_size=40)
    print("Size of rest_acc data " +str(i) + " is %s" %(len(x_train)-tmp))
    tmp = len(x_train)

TOTAL_DATA_SIZE = len(x_train)

for i in range(len(y_train)):
    if y_train[i] is 0:
        y_train[i] = [1,0,0]
    elif y_train[i] is 1:
        y_train[i] = [0,1,0]
    elif y_train[i] is 2:
        y_train[i] = [0,0,1]


combine = list(zip(x_train, y_train))
shuffle(combine)
x_train, y_train = zip(*combine)
x_train = np.asarray(x_train)
y_train = np.asarray(y_train)
x_train = x_train.reshape(TOTAL_DATA_SIZE,40,3)
y_train = y_train.reshape(TOTAL_DATA_SIZE,3)
print(np.shape(x_train))
print(np.shape(y_train))


model = Sequential([
        Conv1D(filters = 80, kernel_size = 5, activation='relu', input_shape=(40,3), padding='same'),
        MaxPooling1D(pool_size = 4, strides=4, padding='valid'),
        Conv1D(filters = 120, kernel_size = 2, activation='relu', padding='same'),
        MaxPooling1D(pool_size = 2, strides=2, padding='valid'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(3, activation='softmax'),
    ])

model.summary()

model.compile(loss="categorical_crossentropy", optimizer='adam', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=32, validation_split=0.1)


