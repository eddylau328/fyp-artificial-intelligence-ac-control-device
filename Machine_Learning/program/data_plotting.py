import matplotlib.pyplot as plt
import matplotlib.dates as plt_date
import json
from datetime import datetime

def get_data(path, dataname):
    with open(path, 'r') as file:
        json_file = json.load(file)
    return json_file[dataname]

data = get_data('env_train_data.json', 'datapack')

indoor_temp = [dict_obj['temp'] for dict_obj in data]
outdoor_temp = [dict_obj['outdoor_temp'] for dict_obj in data]
set_temp = [dict_obj['set_temp'] for dict_obj in data]
time = [datetime.strptime(dict_obj['time'], '%Y-%m-%d %H:%M:%S.%f') for dict_obj in data]

#time = plt_date.date2num(time)
plt.plot(time, indoor_temp, label='indoor temp')
plt.plot(time, outdoor_temp, label='outdoor temp')
plt.plot(time, set_temp, label='set temp')
plt.legend()
plt.show()
