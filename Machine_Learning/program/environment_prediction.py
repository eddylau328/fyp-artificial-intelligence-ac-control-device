import time
import numpy as np
from datetime import datetime
from libs import temperature_prediction_model as temperature_model
from libs import humidity_prediction_model as humidity_model
from libs import skin_temp_prediction_model as skin_temp_model

inputs = [{
   "body": 33.091346741,
   "feedback": "acceptable",
   "hum": 75.800003052,
   "light": 27.5,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.600000000000023,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 0,
   "temp": 27.5,
   "time": "2020-04-21 22:24:45.171736"
  },
  {
   "body": 33.697917938,
   "feedback": "acceptable",
   "hum": 73,
   "light": 27.5,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 1,
   "temp": 27.300001144,
   "time": "2020-04-21 22:25:19.613320"
  },
  {
   "body": 33.854167938,
   "feedback": "Hot",
   "hum": 69.700004578,
   "light": 26.666671753,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 2,
   "temp": 27.200000763,
   "time": "2020-04-21 22:25:52.739973"
  },
  {
   "body": 33.849998474,
   "feedback": "acceptable",
   "hum": 66.599998474,
   "light": 27.5,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 3,
   "temp": 27,
   "time": "2020-04-21 22:26:27.102749"
  },
  {
   "body": 33.849998474,
   "feedback": "acceptable",
   "hum": 64.099998474,
   "light": 27.5,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 4,
   "temp": 26.800001144,
   "time": "2020-04-21 22:27:02.476118"
  },
  {
   "body": 33.875,
   "feedback": "acceptable",
   "hum": 61.700000763,
   "light": 28.333330154,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 5,
   "temp": 26.600000381,
   "time": "2020-04-21 22:27:37.992238"
  },
  {
   "body": 33.833332062,
   "feedback": "acceptable",
   "hum": 59.900001526,
   "light": 28.333330154,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 6,
   "temp": 26.399999619,
   "time": "2020-04-21 22:28:11.864880"
  },
  {
   "body": 33.775001526,
   "feedback": "acceptable",
   "hum": 58.5,
   "light": 29.166671753,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 7,
   "temp": 26.200000763,
   "time": "2020-04-21 22:28:47.837357"
  },
  {
   "body": 33.65625,
   "feedback": "acceptable",
   "hum": 57.400001526,
   "light": 28.333330154,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 8,
   "temp": 26,
   "time": "2020-04-21 22:29:23.124736"
  },
  {
   "body": 33.549999237,
   "feedback": "acceptable",
   "hum": 56.400001526,
   "light": 28.333330154,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 9,
   "temp": 25.800001144,
   "time": "2020-04-21 22:29:58.189646"
  },
  {
   "body": 33.427082062,
   "feedback": "A Bit Hot",
   "hum": 55.5,
   "light": 28.333330154,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.590000000000032,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 10,
   "temp": 25.700000763,
   "time": "2020-04-21 22:30:32.726589"
  },
  {
   "body": 33.375,
   "feedback": "acceptable",
   "hum": 54.100002289,
   "light": 28.333330154,
   "move_type": "work",
   "outdoor_des": "few clouds",
   "outdoor_hum": 74,
   "outdoor_press": 101.3,
   "outdoor_temp": 25.600000000000023,
   "press": 101.300003052,
   "set_fanspeed": 3,
   "set_temp": 19,
   "stepNo": 11,
   "temp": 25.5,
   "time": "2020-04-21 22:31:07.328459"
  }]

temp_predict_model = temperature_model.create_model()
temp_predict_model.load_model(path="temperature_prediction_models/prediction_model_1.h5")
hum_predict_model = humidity_model.create_model()
hum_predict_model.load_model(path="humidity_prediction_models/prediction_model_1.h5")
skin_temp_model = skin_temp_model.create_model()
skin_temp_model.load_model(path="skin_temperature_prediction_models/prediction_model_1.h5")

inputs = inputs[0:2]

str_pre_time, str_curr_time = inputs[0]['time'], inputs[1]['time']
pre_time = datetime.strptime(str_pre_time, '%Y-%m-%d %H:%M:%S.%f')
curr_time = datetime.strptime(str_curr_time, '%Y-%m-%d %H:%M:%S.%f')
predict_delta_time = (curr_time-pre_time).seconds + 30.0
predict_time = (curr_time-pre_time).seconds
predict_temp = temp_predict_model.predict(inputs, predict_delta_time, predict_time)
predict_hum = hum_predict_model.predict(inputs, predict_delta_time, predict_time)
predict_body = skin_temp_model.predict(inputs, predict_delta_time, predict_time)
outdoor_temp, outdoor_hum = inputs[1]['outdoor_temp'], inputs[1]['outdoor_hum']

previous_data_pkg = {
    'temp': inputs[1]['temp'],
    'hum': inputs[1]['hum'],
    'outdoor_temp': inputs[1]['outdoor_temp'],
    'outdoor_hum': inputs[1]['outdoor_hum'],
    'set_temp' : inputs[1]['set_temp'],
    'set_fanspeed': inputs[1]['set_fanspeed'],
    'body': inputs[1]['body']
}
current_data_pkg = {
    'temp': predict_temp,
    'hum': predict_hum,
    'outdoor_temp': outdoor_temp,
    'outdoor_hum': outdoor_hum,
    'body': predict_body,
    'set_temp':19,
    'set_fanspeed':3
}

for i in range(10):
    pkg = [previous_data_pkg, current_data_pkg]
    predict_delta_time = 60.0   # previous + predict = 30s + 30s = 60s
    predict_time = 30.0
    predict_temp = temp_predict_model.predict(pkg, predict_delta_time, predict_time)
    predict_hum = hum_predict_model.predict(pkg, predict_delta_time, predict_time)
    predict_body = skin_temp_model.predict(pkg, predict_delta_time, predict_time)
    outdoor_temp, outdoor_hum = current_data_pkg['outdoor_temp'], current_data_pkg['outdoor_hum']
    previous_data_pkg = current_data_pkg
    print(current_data_pkg['temp'],predict_temp)
    print(current_data_pkg['hum'], predict_hum)
    print(current_data_pkg['body'], predict_body)
    print(current_data_pkg['set_temp'], current_data_pkg['set_fanspeed'])
    current_data_pkg = {
        'temp': predict_temp,
        'hum': predict_hum,
        'outdoor_temp': outdoor_temp,
        'outdoor_hum': outdoor_hum,
        'body': predict_body,
        'set_temp':previous_data_pkg['set_temp'],
        'set_fanspeed':previous_data_pkg['set_fanspeed']
    }

print(current_data_pkg['temp'],current_data_pkg['hum'],current_data_pkg['body'])
