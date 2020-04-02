import matplotlib.pyplot as plt
import matplotlib.dates as plt_date
import json
import numpy as np
from datetime import datetime

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

datapack = []
for i in range(1, num_of_paths()+1):
    datapack.append(get_data('env_training_data/env_data_'+str(i)+'.json', 'datapack'))

data = []
for pack in datapack:
    for dict_obj in pack:
        data.append(dict_obj)

indoor_temp = []
for dict_obj in data:
    indoor_temp.append(dict_obj['temp'])

indoor_hum = []
for dict_obj in data:
    indoor_hum.append(dict_obj['hum'])

body_temp = []
for dict_obj in data:
    body_temp.append(dict_obj['body'])

feedback = []
for dict_obj in data:
    feedback.append(dict_obj['feedback'])

i = 0
while(i < (len(feedback)-1)):
    if (feedback[i] != "acceptable"):
        for j in range(1, 5):
            if (i+j > len(feedback)-1):
                i = i+j
                break
            if (feedback[i+j] == "acceptable"):
                feedback[i+j] = feedback[i]
            else:
                i = i+j
                break
    i += 1

feedback = np.array(feedback)


indoor = np.array([indoor_temp,indoor_hum,body_temp]).T

print(indoor.shape)
print(feedback.shape)

very_hot = np.where(feedback == "Very Hot")
very_hot = indoor[very_hot]
print(very_hot.shape)
hot = np.where(feedback == "Hot")
hot = indoor[hot]
print(hot.shape)
a_bit_hot = np.where(feedback == "A Bit Hot")
a_bit_hot = indoor[a_bit_hot]
print(a_bit_hot.shape)
comfy = np.where(feedback == "Comfy")
comfy = indoor[comfy]
print(comfy.shape)
acceptable = np.where(feedback == "acceptable")
acceptable = indoor[acceptable]
print(acceptable.shape)
a_bit_cold = np.where(feedback == "A Bit Cold")
a_bit_cold = indoor[a_bit_cold]
print(a_bit_cold.shape)
cold = np.where(feedback == "Cold")
cold = indoor[cold]
print(cold.shape)
very_cold = np.where(feedback == "Very Cold")
very_cold = indoor[very_cold]
print(very_cold.shape)

#set_temp = [dict_obj['set_temp'] for dict_obj in data]
#time = [datetime.strptime(dict_obj['time'], '%Y-%m-%d %H:%M:%S.%f') for dict_obj in data]

#time = plt_date.date2num(time)

#ax = plt.axes(projection='3d')
#plt.scatter(hot[:,0], hot[:,1])
#plt.scatter(a_bit_hot[:,0], a_bit_hot[:,1])



ax = plt.axes(projection='3d')
ax.set_xlim(15,30)
ax.set_ylim(40,100)
ax.set_zlim(28,38)
ax.scatter3D(very_hot[:,0], very_hot[:,1],very_hot[:,2], color='darkred', label='very hot')
ax.scatter3D(hot[:,0], hot[:,1],hot[:,2], color='red', label='hot')
ax.scatter3D(a_bit_hot[:,0], a_bit_hot[:,1],a_bit_hot[:,2], color='lightcoral', label='a_bit_hot')
ax.scatter3D(acceptable[:,0], acceptable[:,1],acceptable[:,2], color='grey', label='acceptable')
ax.scatter3D(a_bit_cold[:,0], a_bit_cold[:,1],a_bit_cold[:,2], color='lightblue', label='a bit cold')
ax.scatter3D(cold[:,0], cold[:,1],cold[:,2], color='blue', label='cold')
ax.scatter3D(very_cold[:,0], very_cold[:,1],very_cold[:,2], color='darkblue', label='very cold')
ax.scatter3D(comfy[:,0], comfy[:,1],comfy[:,2], color='lime', label='comfy')
plt.show()

ax = plt.axes(projection='3d')
ax.set_xlim(15,30)
ax.set_ylim(40,100)
ax.set_zlim(28,38)
ax.scatter3D(very_hot[:,0], very_hot[:,1],very_hot[:,2], color='darkred', label='very hot')
ax.scatter3D(hot[:,0], hot[:,1],hot[:,2], color='red', label='hot')
ax.scatter3D(a_bit_hot[:,0], a_bit_hot[:,1],a_bit_hot[:,2], color='lightcoral', label='a_bit_hot')
#ax.scatter3D(acceptable[:,0], acceptable[:,1],acceptable[:,2], color='grey', label='acceptable')
ax.scatter3D(a_bit_cold[:,0], a_bit_cold[:,1],a_bit_cold[:,2], color='lightblue', label='a bit cold')
ax.scatter3D(cold[:,0], cold[:,1],cold[:,2], color='blue', label='cold')
ax.scatter3D(very_cold[:,0], very_cold[:,1],very_cold[:,2], color='darkblue', label='very cold')
ax.scatter3D(comfy[:,0], comfy[:,1],comfy[:,2], color='lime', label='comfy')
plt.show()


##########################################
#
#   Remarks
#   env_data_7.json is sleep data, but i forgot to turn off the other fan, with fanspeed 1
#
##########################################
