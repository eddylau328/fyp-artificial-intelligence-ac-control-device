import json
import random

MAX_MIN_TABLE = {
    'temp' : (28.6, 19.0),
    'hum' : (87.8, 39.5),
    'outdoor_temp' : (27.67, 19.0),
    'outdoor_hum' : (100.0, 26.0),
    'body' : (34.75, 29.4375)
}

def export(data, dataname, filename, indent=1):
  pack = {}
  pack[dataname] = data
  with open(filename+'.json', 'w') as outfile:
    json.dump(pack, outfile, indent=indent)
    print("Exported json file <%s>" %filename)


points = []

for i in range(1,100):
  dict_obj = {
   "body": 32.92307663+i*0.01 + random.uniform(-1, 1),
   "feedback": "Very Hot",
   "hum": 63.799999237+i*0.13 + random.uniform(-1, 1),
   "light": 27.5,
   "move_type": "rest",
   "outdoor_des": "clear sky",
   "outdoor_hum": 74 +i*0.076+ random.uniform(-1, 1),
   "outdoor_press": 103.6,
   "outdoor_temp": 26.360000000000014 +i*0.007+ random.uniform(-1, 1),
   "press": 101.099998474,
   "set_fanspeed": random.randint(1,3),
   "set_temp": 25,
   "stepNo": i-1,
   "temp": 27.899999619 +0.004*i+ random.uniform(-1, 1),
   "time": "2020-04-20 18:58:19.444283"
  }
  points.append(dict_obj)

for i in range(1, 100):
  dict_obj = {
   "body": 33.375+i*0.006 + random.uniform(-1, 1),
   "feedback": "Hot",
   "hum": 63.799999237+i*0.13 + random.uniform(-1, 1),
   "light": 34.166660309,
   "move_type": "work",
   "outdoor_des": "clear sky",
   "outdoor_hum": 60 +i*0.047+ random.uniform(-1, 1),
   "outdoor_press": 101.7,
   "outdoor_temp": 21.620000000000005 +i*0.03+ random.uniform(-1, 1),
   "press": 101.800003052,
   "set_fanspeed": 3,
   "set_temp": 25,
   "stepNo": i - 1 + 100,
   "temp": 24.800001144+0.02*i+ random.uniform(-1, 1),
   "time": "2020-04-09 21:05:19.880857"
  }
  points.append(dict_obj)

filename = 'env_training_data/env_data_24'
export(data=points,dataname='datapack',filename=filename)

