import json
from enum import Enum
from random import shuffle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv1D, MaxPooling1D
import sys
sys.setrecursionlimit(1500)

class MovementType(Enum):
    work = 0
    rest = 1
    sleep = 2
    move = 3


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


def copy_list(dict_list, size, cover_size):

    counter = 0
    copy_dict_list = []
    while ((counter+size) <= len(dict_list)):
        for obj in dict_list[counter:counter+size]:
            copy_dict_list.append(obj)
        counter += cover_size

    iterate = 1
    acc_x, acc_y, acc_z = [], [], []
    x = []

    for j in range(len(copy_dict_list)):
        dict_obj = copy_dict_list[j]
        acc_x.append(dict_obj['acc_x'])
        acc_y.append(dict_obj['acc_y'])
        acc_z.append(dict_obj['acc_z'])
        if (iterate == size):
            x.append([acc_x,acc_y,acc_z])
            acc_x, acc_y, acc_z = [], [], []
            iterate = 1
        else:
            iterate += 1

    return x


def transform_2_train_data(dict_list, size, y_value, x_train, y_train, overlap, overlap_size):
    if(overlap == False):
        cover_size = size
    else:
        if (overlap_size >= 0 and overlap_size < size):
            cover_size = size - overlap_size
        else:
            print("Error in transform_2_train_data")
            return

    x = copy_list(dict_list, size, cover_size)
    y = [y_value for i in range(len(x))]

    for data in x:
        x_train.append(data)
    for data in y:
        y_train.append(data)

    return x_train, y_train



MOVE_DATA_SIZE = 1
WORK_DATA_SIZE = 3
SLEEP_DATA_SIZE = 3
REST_DATA_SIZE = 3

PERIOD_SIZE = 20    # 4Hz => 4Hz * sec = PERIOD_SIZE
OVERLAP_DATA = False
OVERLAP_SIZE = 0

#move_acc = []
#for i in range(MOVE_DATA_SIZE):
#    move_acc.append(process_data(get_data("smartwatch_data/move_acc_4hz_"+str(i)+".json", "acc")))
#    print("Size of move_acc data "+str(i) + " is %s" %(len(move_acc[i])))


work_acc = []
for i in range(WORK_DATA_SIZE):
    work_acc.append(process_data(get_data("smartwatch_data/work_acc_4hz_"+str(i)+".json", "acc")))
    print("Size of work_acc data "+str(i) + " is %s" %(len(work_acc[i])))

sleep_acc = []
for i in range(SLEEP_DATA_SIZE):
    sleep_acc.append(process_data(get_data("smartwatch_data/sleep_acc_4hz_"+str(i)+".json", "acc")))
    print("Size of sleep_acc data "+str(i) + " is %s" %(len(sleep_acc[i])))

rest_acc = []
for i in range(REST_DATA_SIZE):
    rest_acc.append(process_data(get_data("smartwatch_data/rest_acc_4hz_"+str(i)+".json", "acc")))
    print("Size of rest_acc data "+str(i) + " is %s" %(len(rest_acc[i])))


x_train, y_train = [], []
tmp = 0

#for i in range(MOVE_DATA_SIZE):
#    x_train, y_train = transform_2_train_data(move_acc[i], PERIOD_SIZE, MovementType.move.value, x_train, y_train, overlap=OVERLAP_DATA, overlap_size=OVERLAP_SIZE)
#    print("Number of period of move_acc data "+str(i) + " is %s" %(len(x_train)-tmp))
#    tmp = len(x_train)

for i in range(WORK_DATA_SIZE):
    x_train, y_train = transform_2_train_data(work_acc[i], PERIOD_SIZE, MovementType.work.value, x_train, y_train, overlap=OVERLAP_DATA, overlap_size=OVERLAP_SIZE)
    print("Number of period of work_acc data "+str(i) + " is %s" %(len(x_train)-tmp))
    tmp = len(x_train)

for i in range(SLEEP_DATA_SIZE):
    x_train, y_train = transform_2_train_data(sleep_acc[i], PERIOD_SIZE, MovementType.sleep.value, x_train, y_train, overlap=OVERLAP_DATA, overlap_size=OVERLAP_SIZE)
    print("Number of period of sleep_acc data "+str(i) + " is %s" %(len(x_train)-tmp))
    tmp = len(x_train)

for i in range(REST_DATA_SIZE):
    x_train, y_train = transform_2_train_data(rest_acc[i], PERIOD_SIZE, MovementType.rest.value, x_train, y_train, overlap=OVERLAP_DATA, overlap_size=OVERLAP_SIZE)
    print("Number of period of rest_acc data " +str(i) + " is %s" %(len(x_train)-tmp))
    tmp = len(x_train)

TOTAL_DATA_SIZE = len(x_train)
print("The total data size is %s" %TOTAL_DATA_SIZE)

#for i in range(len(y_train)):
#    if y_train[i] is 0:
#        y_train[i] = [1,0,0,0]
#    elif y_train[i] is 1:
#        y_train[i] = [0,1,0,0]
#    elif y_train[i] is 2:
#        y_train[i] = [0,0,1,0]
#    elif y_train[i] is 3:
#        y_train[i] = [0,0,0,1]


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
x_train = x_train.reshape(TOTAL_DATA_SIZE,PERIOD_SIZE,3)
y_train = y_train.reshape(TOTAL_DATA_SIZE,3)
print(np.shape(x_train))
print(np.shape(y_train))


model = Sequential([
        Conv1D(filters = 64, kernel_size = 5, activation='relu', input_shape=(PERIOD_SIZE,3), padding='same'),
        MaxPooling1D(pool_size = 4, strides=4, padding='valid'),
        Conv1D(filters = 128, kernel_size = 2, activation='relu', padding='same'),
        MaxPooling1D(pool_size = 2, strides=2, padding='valid'),
        Flatten(),
        Dense(64, activation='relu'),
        Dense(3, activation='softmax'),
    ])

model.summary()

model.compile(loss="categorical_crossentropy", optimizer='adam', metrics=['accuracy'])

model.fit(x_train, y_train, batch_size=32, validation_split=0.1)


