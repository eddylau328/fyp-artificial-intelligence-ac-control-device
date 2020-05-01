from psychrochart import PsychroChart
import matplotlib.pyplot as plt
import matplotlib.dates as plt_date
import json
import numpy as np
import pandas as pd
import seaborn as sn
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

def normalize_data(x, method):
    if (method == "min_max"):
        max, min = x[:].max(), x[:].min()
        #print(max, min)
        x[:] = (x[:]-min)/(max-min)
    elif(method == "mean_std"):
        mean, std = np.mean(x[:]), np.std(x[:])
        x[:] = (x[:]-mean)/std
    return x


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

data = amplify_feedback(data, True, feedback_amplifier=4)

indoor_temp = []
for dict_obj in data:
    indoor_temp.append(dict_obj['temp'])

indoor_hum = []
for dict_obj in data:
    indoor_hum.append(dict_obj['hum'])

body_temp = []
for dict_obj in data:
    body_temp.append(dict_obj['body'])

outdoor_temp = []
for dict_obj in data:
    outdoor_temp.append(dict_obj['outdoor_temp'])

outdoor_hum = []
for dict_obj in data:
    outdoor_hum.append(dict_obj['outdoor_hum'])

outdoor_press = []
for dict_obj in data:
    outdoor_press.append(dict_obj['outdoor_press'])

indoor_press = []
for dict_obj in data:
    indoor_press.append(dict_obj['press'])

light_intensity = []
for dict_obj in data:
    light_intensity.append(dict_obj['light'])

set_temp = []
for dict_obj in data:
    set_temp.append(dict_obj['set_temp'])

set_fanspeed = []
for dict_obj in data:
    set_fanspeed.append(dict_obj['set_fanspeed'])

stepNo = []
for dict_obj in data:
    stepNo.append(dict_obj['stepNo'])

time = []
for dict_obj in data:
    time.append(dict_obj['time'])

move = []
for dict_obj in data:
    if (dict_obj['move_type'] == "work"):
        move.append(0)
    elif (dict_obj['move_type'] == "rest"):
        move.append(1)
    else:
        move.append(2)

feedback = []
for dict_obj in data:
    feedback.append(dict_obj['feedback'])

total_feedback = np.array(feedback)

total_indoor = np.array([indoor_temp,indoor_hum,body_temp,set_fanspeed,set_temp, move, outdoor_temp, outdoor_hum, outdoor_press, indoor_press, light_intensity]).T
indoor = np.copy(total_indoor)
feedback = np.copy(total_feedback)

#for i in range(0, 3):
#    indoor[:,i] = normalize_data(indoor[:,i], method="mean_std")

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
plt.title("Indoor Temperature vs Indoor Humidity vs Skin Temperature")
ax.set_xlabel('Indoor Temperature')
ax.set_ylabel('Indoor Humidity')
ax.set_zlabel('Skin Temperature')
#ax.set_xlim(15,30)
#ax.set_ylim(40,100)
#ax.set_zlim(28,38)
ax.scatter3D(very_hot[:,0], very_hot[:,1],very_hot[:,2], color='darkred', label='very hot')
ax.scatter3D(hot[:,0], hot[:,1],hot[:,2], color='red', label='hot')
ax.scatter3D(a_bit_hot[:,0], a_bit_hot[:,1],a_bit_hot[:,2], color='lightcoral', label='a bit hot')
#ax.scatter3D(acceptable[:,0], acceptable[:,1],acceptable[:,2], color='grey', label='acceptable')
ax.scatter3D(a_bit_cold[:,0], a_bit_cold[:,1],a_bit_cold[:,2], color='lightblue', label='a bit cold')
ax.scatter3D(cold[:,0], cold[:,1],cold[:,2], color='blue', label='cold')
ax.scatter3D(very_cold[:,0], very_cold[:,1],very_cold[:,2], color='darkblue', label='very cold')
ax.scatter3D(comfy[:,0], comfy[:,1],comfy[:,2], color='lime', label='comfy')
plt.legend()
plt.show()

'''
norm_indoor = normalize_data(np.array(indoor_temp))
norm_hum = normalize_data(np.array(indoor_hum))

plt.plot([i for i in range(len(indoor_temp))], norm_indoor, label="temp")
plt.plot([i for i in range(len(indoor_temp))], norm_hum, label="hum")
plt.legend()
plt.show()
'''

fig = plt.figure()
plt.subplot(1, 3, 1)
plt.title("Skin Temperature vs Indoor Temperature")
plt.xlabel("Skin Temperature")
plt.ylabel("Indoor Temperature")
plt.scatter(very_hot[:,2], very_hot[:,0], color='darkred', label='very hot')
plt.scatter(hot[:,2],hot[:,0], color='red', label='hot')
plt.scatter(a_bit_hot[:,2], a_bit_hot[:,0], color='lightcoral', label='a bit hot')
#plt.scatter(acceptable[:,2], acceptable[:,0], color='grey', label='acceptable')
plt.scatter(a_bit_cold[:,2], a_bit_cold[:,0], color='lightblue', label='a bit cold')
plt.scatter(cold[:,2], cold[:,0], color='blue', label='cold')
plt.scatter(very_cold[:,2], very_cold[:,0], color='darkblue', label='very cold')
plt.scatter(comfy[:,2], comfy[:,0], color='lime', label='comfy')
plt.subplot(1, 3, 2)
plt.title("Skin Temperature vs Indoor Humidity")
plt.xlabel("Skin Temperature")
plt.ylabel("Indoor Humidity")
plt.scatter(very_hot[:,2], very_hot[:,1], color='darkred', label='very hot')
plt.scatter(hot[:,2],hot[:,1], color='red', label='hot')
plt.scatter(a_bit_hot[:,2], a_bit_hot[:,1], color='lightcoral', label='a bit hot')
#plt.scatter(acceptable[:,2], acceptable[:,0], color='grey', label='acceptable')
plt.scatter(a_bit_cold[:,2], a_bit_cold[:,1], color='lightblue', label='a bit cold')
plt.scatter(cold[:,2], cold[:,1], color='blue', label='cold')
plt.scatter(very_cold[:,2], very_cold[:,1], color='darkblue', label='very cold')
plt.scatter(comfy[:,2], comfy[:,1], color='lime', label='comfy')

plt.subplot(1, 3, 3)
plt.title("Indoor Temperature vs Indoor Humidity")
plt.xlabel("Indoor Temperature")
plt.ylabel("Indoor Humidity")
plt.scatter(very_hot[:,0], very_hot[:,1], color='darkred', label='very hot')
plt.scatter(hot[:,0],hot[:,1], color='red', label='hot')
plt.scatter(a_bit_hot[:,0], a_bit_hot[:,1], color='lightcoral', label='a bit hot')
#plt.scatter(acceptable[:,2], acceptable[:,0], color='grey', label='acceptable')
plt.scatter(a_bit_cold[:,0], a_bit_cold[:,1], color='lightblue', label='a bit cold')
plt.scatter(cold[:,0], cold[:,1], color='blue', label='cold')
plt.scatter(very_cold[:,0], very_cold[:,1], color='darkblue', label='very cold')
plt.scatter(comfy[:,0], comfy[:,1], color='lime', label='comfy')
plt.legend()
plt.show()

BINS = 25
SKIN_TEMP_RANGE = [29,35]

fig = plt.figure()
fig.subplots_adjust(hspace=0.7, wspace=0.08)
ax1 = fig.add_subplot(4,2,1)
ax1.set_title("Distribution of Very Hot Data")
ax1.set_xlabel("Skin Temperature")
ax1.set_ylabel("No. of Feedback")
ax1.hist(very_hot[:,2],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='darkred', label='very hot')
ax1.legend()
ax2 = fig.add_subplot(4,2,3)
ax2.set_title("Distribution of Hot Data")
ax2.set_xlabel("Skin Temperature")
ax2.set_ylabel("No. of Feedback")
ax2.hist(hot[:,2],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='red', label='hot')
ax2.legend()
ax3 = fig.add_subplot(4,2,5)
ax3.set_title("Distribution of A Bit Hot Data")
ax3.set_xlabel("Skin Temperature")
ax3.set_ylabel("No. of Feedback")
ax3.hist(a_bit_hot[:,2],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lightcoral', label='a bit hot')
ax3.legend()
ax4 = fig.add_subplot(4,2,2)
ax4.set_title("Distribution of Very Cold Data")
ax4.set_xlabel("Skin Temperature")
#ax4.set_ylabel("No. of Feedback")
ax4.hist(very_cold[:,2],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='darkblue', label='very cold')
ax4.legend()
ax5 = fig.add_subplot(4,2,4)
ax5.set_title("Distribution of Cold Data")
ax5.set_xlabel("Skin Temperature")
#ax5.set_ylabel("No. of Feedback")
ax5.hist(cold[:,2],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='blue', label='cold')
ax5.legend()
ax6 = fig.add_subplot(4,2,6)
ax6.set_title("Distribution of A Bit Cold Data")
ax6.set_xlabel("Skin Temperature")
#ax6.set_ylabel("No. of Feedback")
ax6.hist(a_bit_cold[:,2],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lightblue', label='a bit cold')
ax6.legend()
ax7 = fig.add_subplot(4,2,7)
ax7.set_title("Distribution of Comfy Data")
ax7.set_xlabel("Skin Temperature")
ax7.set_ylabel("No. of Feedback")
ax7.hist(comfy[:,2],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lime', label='comfy')
ax7.legend()
plt.show()

feedback_dict = {
    'very_cold':np.around(np.mean(very_cold[:,2]), decimals=2),
    'cold':np.around(np.mean(cold[:,2]), decimals=2),
    'a_bit_cold':np.around(np.mean(a_bit_cold[:,2]), decimals=2),
    'very_hot':np.around(np.mean(very_hot[:,2]), decimals=2),
    'hot':np.around(np.mean(hot[:,2]), decimals=2),
    'a_bit_hot':np.around(np.mean(a_bit_hot[:,2]), decimals=2),
    'comfy':np.around(np.mean(comfy[:,2]), decimals=2)
}

print(feedback_dict)

feedback_dict = {
    'very_cold':np.around(np.std(very_cold[:,2]), decimals=2),
    'cold':np.around(np.std(cold[:,2]), decimals=2),
    'a_bit_cold':np.around(np.std(a_bit_cold[:,2]), decimals=2),
    'very_hot':np.around(np.std(very_hot[:,2]), decimals=2),
    'hot':np.around(np.std(hot[:,2]), decimals=2),
    'a_bit_hot':np.around(np.std(a_bit_hot[:,2]), decimals=2),
    'comfy':np.around(np.std(comfy[:,2]), decimals=2)
}
print(feedback_dict)

print()

BINS = 25
SKIN_TEMP_RANGE = [16,30]

fig = plt.figure()
fig.subplots_adjust(hspace=0.7, wspace=0.08)
ax1 = fig.add_subplot(4,2,1)
ax1.set_title("Distribution of Very Hot Data")
ax1.set_xlabel("Indoor Temperature")
ax1.set_ylabel("No. of Feedback")
ax1.hist(very_hot[:,0],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='darkred', label='very hot')
ax1.legend()
ax2 = fig.add_subplot(4,2,3)
ax2.set_title("Distribution of Hot Data")
ax2.set_xlabel("Indoor Temperature")
ax2.set_ylabel("No. of Feedback")
ax2.hist(hot[:,0],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='red', label='hot')
ax2.legend()
ax3 = fig.add_subplot(4,2,5)
ax3.set_title("Distribution of A Bit Hot Data")
ax3.set_xlabel("Indoor Temperature")
ax3.set_ylabel("No. of Feedback")
ax3.hist(a_bit_hot[:,0],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lightcoral', label='a bit hot')
ax3.legend()
ax4 = fig.add_subplot(4,2,2)
ax4.set_title("Distribution of Very Cold Data")
ax4.set_xlabel("Indoor Temperature")
#ax4.set_ylabel("No. of Feedback")
ax4.hist(very_cold[:,0],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='darkblue', label='very cold')
ax4.legend()
ax5 = fig.add_subplot(4,2,4)
ax5.set_title("Distribution of Cold Data")
ax5.set_xlabel("Indoor Temperature")
#ax5.set_ylabel("No. of Feedback")
ax5.hist(cold[:,0],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='blue', label='cold')
ax5.legend()
ax6 = fig.add_subplot(4,2,6)
ax6.set_title("Distribution of A Bit Cold Data")
ax6.set_xlabel("Indoor Temperature")
#ax6.set_ylabel("No. of Feedback")
ax6.hist(a_bit_cold[:,0],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lightblue', label='a bit cold')
ax6.legend()
ax7 = fig.add_subplot(4,2,7)
ax7.set_title("Distribution of Comfy Data")
ax7.set_xlabel("Indoor Temperature")
ax7.set_ylabel("No. of Feedback")
ax7.hist(comfy[:,0],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lime', label='comfy')
ax7.legend()
plt.show()

feedback_dict = {
    'very_cold':np.around(np.mean(very_cold[:,0]), decimals=2),
    'cold':np.around(np.mean(cold[:,0]), decimals=2),
    'a_bit_cold':np.around(np.mean(a_bit_cold[:,0]), decimals=2),
    'very_hot':np.around(np.mean(very_hot[:,0]), decimals=2),
    'hot':np.around(np.mean(hot[:,0]), decimals=2),
    'a_bit_hot':np.around(np.mean(a_bit_hot[:,0]), decimals=2),
    'comfy':np.around(np.mean(comfy[:,0]), decimals=2)
}
print(feedback_dict)

feedback_dict = {
    'very_cold':np.around(np.std(very_cold[:,0]), decimals=2),
    'cold':np.around(np.std(cold[:,0]), decimals=2),
    'a_bit_cold':np.around(np.std(a_bit_cold[:,0]), decimals=2),
    'very_hot':np.around(np.std(very_hot[:,0]), decimals=2),
    'hot':np.around(np.std(hot[:,0]), decimals=2),
    'a_bit_hot':np.around(np.std(a_bit_hot[:,0]), decimals=2),
    'comfy':np.around(np.std(comfy[:,0]), decimals=2)
}
print(feedback_dict)

print()

BINS = 25
SKIN_TEMP_RANGE = [40,100]

fig = plt.figure()
fig.subplots_adjust(hspace=0.7, wspace=0.08)
ax1 = fig.add_subplot(4,2,1)
ax1.set_title("Distribution of Very Hot Data")
ax1.set_xlabel("Indoor Humidity")
ax1.set_ylabel("No. of Feedback")
ax1.hist(very_hot[:,1],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='darkred', label='very hot')
ax1.legend()
ax2 = fig.add_subplot(4,2,3)
ax2.set_title("Distribution of Hot Data")
ax2.set_xlabel("Indoor Humidity")
ax2.set_ylabel("No. of Feedback")
ax2.hist(hot[:,1],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='red', label='hot')
ax2.legend()
ax3 = fig.add_subplot(4,2,5)
ax3.set_title("Distribution of A Bit Hot Data")
ax3.set_xlabel("Indoor Humidity")
ax3.set_ylabel("No. of Feedback")
ax3.hist(a_bit_hot[:,1],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lightcoral', label='a bit hot')
ax3.legend()
ax4 = fig.add_subplot(4,2,2)
ax4.set_title("Distribution of Very Cold Data")
ax4.set_xlabel("Indoor Humidity")
#ax4.set_ylabel("No. of Feedback")
ax4.hist(very_cold[:,1],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='darkblue', label='very cold')
ax4.legend()
ax5 = fig.add_subplot(4,2,4)
ax5.set_title("Distribution of Cold Data")
ax5.set_xlabel("Indoor Humidity")
#ax5.set_ylabel("No. of Feedback")
ax5.hist(cold[:,1],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='blue', label='cold')
ax5.legend()
ax6 = fig.add_subplot(4,2,6)
ax6.set_title("Distribution of A Bit Cold Data")
ax6.set_xlabel("Indoor Humidity")
#ax6.set_ylabel("No. of Feedback")
ax6.hist(a_bit_cold[:,1],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lightblue', label='a bit cold')
ax6.legend()
ax7 = fig.add_subplot(4,2,7)
ax7.set_title("Distribution of Comfy Data")
ax7.set_xlabel("Indoor Humidity")
ax7.set_ylabel("No. of Feedback")
ax7.hist(comfy[:,1],bins=BINS,range=SKIN_TEMP_RANGE,density=False,edgecolor='black', color='lime', label='comfy')
ax7.legend()
plt.show()

feedback_dict = {
    'very_cold':np.around(np.mean(very_cold[:,1]),decimals=2),
    'cold':np.around(np.mean(cold[:,1]),decimals=2),
    'a_bit_cold':np.around(np.mean(a_bit_cold[:,1]),decimals=2),
    'very_hot':np.around(np.mean(very_hot[:,1]),decimals=2),
    'hot':np.around(np.mean(hot[:,1]),decimals=2),
    'a_bit_hot':np.around(np.mean(a_bit_hot[:,1]),decimals=2),
    'comfy':np.around(np.mean(comfy[:,1]),decimals=2)
}

print(feedback_dict)

feedback_dict = {
    'very_cold':np.around(np.std(very_cold[:,1]), decimals=2),
    'cold':np.around(np.std(cold[:,1]), decimals=2),
    'a_bit_cold':np.around(np.std(a_bit_cold[:,0]), decimals=2),
    'very_hot':np.around(np.std(very_hot[:,1]), decimals=2),
    'hot':np.around(np.std(hot[:,1]), decimals=2),
    'a_bit_hot':np.around(np.std(a_bit_hot[:,1]), decimals=2),
    'comfy':np.around(np.std(comfy[:,1]), decimals=2)
}
print(feedback_dict)

print()

# HEAT MAP
data_dict = {
        'indoor_temp':indoor_temp,
        'indoor_hum':indoor_hum,
        'indoor_press':indoor_press,
        'outdoor_temp':outdoor_temp,
        'outdoor_hum':outdoor_hum,
        'outdoor_press':outdoor_press,
        'skin_temp':body_temp,
        'move type':move,
        'set_temp':set_temp,
        'set_fanspeed':set_fanspeed
        }


df = pd.DataFrame(data_dict, columns=['indoor_temp','indoor_hum','indoor_press','outdoor_temp','outdoor_hum','outdoor_press','skin_temp','move type','set_temp','set_fanspeed'])

corrMatrix = df.corr(method="spearman")
print(corrMatrix)

plt.title("Correlation Heatmap")
sn.heatmap(corrMatrix, annot=True, )
plt.show()


'''
# Load default style:
custom_style = {
    "figure": {
        "title": "Thermal Comfort Zone, Total",
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

fanspeed = np.where(total_indoor[:,3] == 1)
indoor = np.copy(total_indoor[fanspeed])
feedback = np.copy(total_feedback[fanspeed])

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
        "title": "Thermal Comfort Zone, Fanspeed 1",
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

fanspeed = np.where(total_indoor[:,3] == 2)
indoor = np.copy(total_indoor[fanspeed])
feedback = np.copy(total_feedback[fanspeed])

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
        "title": "Thermal Comfort Zone, Fanspeed 2",
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

fanspeed = np.where(total_indoor[:,3] == 3)
indoor = np.copy(total_indoor[fanspeed])
feedback = np.copy(total_feedback[fanspeed])

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
        "title": "Thermal Comfort Zone, Fanspeed 3",
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
'''

##########################################
#
#   Remarks
#   env_data_7.json is sleep data, but i forgot to turn off the other fan, with fanspeed 1
#
##########################################
