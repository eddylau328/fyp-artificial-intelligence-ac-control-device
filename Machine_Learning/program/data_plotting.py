from psychrochart import PsychroChart
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


# decreasing the acceptable feedback
def amplify_feedback(data, replace_acceptable, feedback_amplifier=4):
    feedback = []
    for dict_obj in data:
        feedback.append(dict_obj['feedback'])

    if (replace_acceptable is True):
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
                        break
                    j += 1
            i += 1
    else:
        i = 0
        while(i < (len(feedback)-1)):
            if (feedback[i] != "acceptable"):
                for j in range(1, feedback_amplifier+1):
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

data = amplify_feedback(data, True)

indoor_temp = []
for dict_obj in data:
    indoor_temp.append(dict_obj['temp'])

indoor_hum = []
for dict_obj in data:
    indoor_hum.append(dict_obj['hum'])

body_temp = []
for dict_obj in data:
    body_temp.append(dict_obj['body'])

set_fanspeed = []
for dict_obj in data:
    set_fanspeed.append(dict_obj['set_fanspeed'])

feedback = []
for dict_obj in data:
    feedback.append(dict_obj['feedback'])

feedback = np.array(feedback)


indoor = np.array([indoor_temp,indoor_hum,body_temp,set_fanspeed]).T
'''
fanspeed_1 = np.where(indoor[:,3] == 1)
indoor = indoor[fanspeed_1]
feedback = feedback[fanspeed_1]
'''

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

# Load default style:
custom_style = {
    "figure": {
        "title": "Thermal Comfort Zone",
    },
    "limits": {
        "range_temp_c": [10, 30],
    },
    "chart_params": {
        "with_constant_rh": True,
        "with_constant_v": False,
        "with_constant_h": True,
        "with_constant_wet_temp": False,
        "with_zones": False
    }
}


def create_points(temp_hum_pair, color):
    points = []
    for pair in temp_hum_pair:
        point = {'interior': {'label': 'Interior',
                               'style': {'color': color,
                                         'marker': 'o', 'markersize': 3},
                               'xy': (pair[0], pair[1])}}
        points.append(point)
    return points

chart = PsychroChart(custom_style)
chart.plot(ax=plt.gca())

temp_hum_pair = very_hot[:,0:2].tolist()
points = create_points(temp_hum_pair, color=[1.0, 0, 0, 0.9])
for point in points:
    chart.plot_points_dbt_rh(point)


temp_hum_pair = hot[:,0:2].tolist()
points = create_points(temp_hum_pair, color=[1.0, 0.4, 0.4, 0.9])
for point in points:
    chart.plot_points_dbt_rh(point)


temp_hum_pair = a_bit_hot[:,0:2].tolist()
points = create_points(temp_hum_pair, color=[1.0, 0.8, 0.8, 0.9])
for point in points:
    chart.plot_points_dbt_rh(point)


temp_hum_pair = a_bit_cold[:,0:2].tolist()
points = create_points(temp_hum_pair, color=[0.6, 0.8, 1.0, 0.9])
for point in points:
    chart.plot_points_dbt_rh(point)


temp_hum_pair = cold[:,0:2].tolist()
points = create_points(temp_hum_pair, color=[0.4, 0.698, 1.0, 0.9])
for point in points:
    chart.plot_points_dbt_rh(point)


temp_hum_pair = very_cold[:,0:2].tolist()
points = create_points(temp_hum_pair, color=[0.0, 0.502, 1.0, 0.9])
for point in points:
    chart.plot_points_dbt_rh(point)


temp_hum_pair = comfy[:,0:2].tolist()
points = create_points(temp_hum_pair, color=[0.592, 0.745, 0.051, 0.9])
for point in points:
    chart.plot_points_dbt_rh(point)


plt.show()


##########################################
#
#   Remarks
#   env_data_7.json is sleep data, but i forgot to turn off the other fan, with fanspeed 1
#
##########################################
