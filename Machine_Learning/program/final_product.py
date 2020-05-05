from libs.ac_host import AC_host
from libs.timer import Timer
from datetime import datetime
import supervised_learning as supervised_model
import json
import numpy as np

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


def get_all_data():
    data = []
    for i in range(1, num_of_paths()+1):
        data.append(get_data('env_training_data/env_data_'+str(i)+'.json', 'datapack'))
    datapack = []
    for pack in data:
        for dict_obj in pack:
            datapack.append(dict_obj)
    data = []
    for dict_obj in datapack:
        if (dict_obj['stepNo'] == 0):
            start_time = datetime.strptime(dict_obj['time'], '%Y-%m-%d %H:%M:%S.%f')
            start_time = np.datetime64(start_time)
        time_data = datetime.strptime(dict_obj['time'], '%Y-%m-%d %H:%M:%S.%f')
        time_data = np.datetime64(time_data)
        time_stamp = (time_data - start_time)/np.timedelta64(1, 's')
        data.append([dict_obj['temp'],dict_obj['hum'],dict_obj['outdoor_temp'],dict_obj['outdoor_hum'],dict_obj['body'],dict_obj['set_temp'],dict_obj['set_fanspeed'],time_stamp])
    return np.array(data)


def cosine_similarity(a, b, norms):
    return np.dot(a,b)/(norms*np.linalg.norm(b))


def get_future_point(environment_data, history, norms):
    input_vector = np.array([environment_data['temp'],environment_data['hum'],environment_data['outdoor_temp'],environment_data['outdoor_hum'],environment_data['body'],environment_data['set_temp'],environment_data['set_fanspeed']])
    similarity_list = cosine_similarity(history[:,0:7],input_vector, norms)
    sorted_index = similarity_list.argsort()[::-1]
    extract_data = np.zeros((100,9))
    extract_data[:,0:8] = np.copy(history[sorted_index][:100])
    extract_data[:,8] = np.copy(sorted_index[:100])
    extract_data = np.copy(extract_data[extract_data[:,5] == input_vector[5]])
    extract_data = np.copy(extract_data[extract_data[:,6] == input_vector[6]])

    if (extract_data.size == 0):
        #print("no similar point found")
        return [0, 0, 0]
    else:
        similarity_list = cosine_similarity(extract_data[:,0:7],input_vector, np.linalg.norm(extract_data[:,0:7], axis=1))
        sorted_index = similarity_list.argsort()[::-1]
        extract_data = np.copy(extract_data[sorted_index])
        temp_hum_pair = [0, 0, 0]
        #print("similar point = {}".format(extract_data[0]))
        # extract_data[0][8] is the index, extract_data[0][7] is delta time
        start_time = extract_data[0][7]
        for i in range(int(extract_data[0][8]), history.shape[0]):
            if (history[i][5] != input_vector[5] and history[i][6] != input_vector[6]):
                break
            else:
                temp_hum_pair[0] = history[i][0]
                temp_hum_pair[1] = history[i][1]
                temp_hum_pair[2] += (history[i][7]-start_time)
                start_time = history_data[i][7]
        #print(temp_hum_pair)
        return temp_hum_pair


def control_algorithm(thermal_comfort_model, data_pkg, history, norms):
    current_state_list = np.array([[data_pkg['temp'], data_pkg['hum']
                                , data_pkg['outdoor_temp'], data_pkg['outdoor_hum'], data_pkg['body']
                                , 0, i%3+1] for i in range(27)])
    for i in range(9):
        for j in range(3):
            current_state_list[i*3+j][5] = 17+i
    print()
    print(current_state_list)
    print()
    sorted_list, first_prob_comfy = thermal_comfort_model.predict(data_pkg)
    sorted_list, first_prob_comfy = np.array(sorted_list), np.array(first_prob_comfy)
    sorted_list[:,0], sorted_list[:,1] = sorted_list[:,0] + 17, sorted_list[:,1] + 1
    future_points = np.zeros((sorted_list.shape[0],3))
    for i in range(sorted_list.shape[0]):
        data_pkg['set_temp'], data_pkg['set_fanspeed'] = sorted_list[i][0], sorted_list[i][1]
        future_points[i] = np.array(get_future_point(data_pkg, history, norms))
    future_feedback = np.zeros(first_prob_comfy.shape)
    for i in range(future_points.shape[0]):
        if (future_points[i][0] != 0 and future_points[i][1] != 0):
            data_pkg['temp'], data_pkg['hum'] = future_points[i][0], future_points[i][1]
            future_feedback[i] = thermal_comfort_model.predict(data_pkg, [sorted_list[i][0], sorted_list[i][1]])
        else:
            future_feedback[i] = -1.0
    #print(future_feedback)
    record_table = np.zeros((27,9))
    record_table[:,0:2] = sorted_list
    record_table[:,2:4] = current_state_list[:,0:2]
    record_table[:,4:7] = future_points
    record_table[:,7] = first_prob_comfy
    record_table[:,8] = future_feedback
    print()
    print(record_table)
    print()
    #return best_action


def main():
    host = AC_host(ac_serial_num="fyp0001",watch_serial_num="watch0001")
    # every 60 seconds it will request a data
    host.data_request_seconds = 60
    # every 5 * 60 sec it will do an action
    host.steps_caculation_period = 5
    model = supervised_model.create_model()
    model.load_model()
    # history_data is in numpy array
    history_data = get_all_data()
    history_norm = np.copy(np.linalg.norm(history_data[:,1:7]))
    # if terminate program is true, then this program will be terminated
    # terminate_program could only be changed on the firebase database
    while (host.check_terminate_program()):
        # this is used to do action at the first time
        first_action = True
        # if start ac is true, then the air conditioner should be turn on
        # start_ac is a button for the user to start the air conditioner on the mobile app
        print("Waiting User start AC")
        while (host.check_start_ac()):
            pass
        # for turning on the air conditioner
        if (host.power_state is False):
            if (host.check_action_done()):
                host.ac_power_switch(True)
            print("Waiting AC Remote response")
            while(not host.check_action_done()):
                pass
            host.update_ac_status()
            print("AC is switched ON")

        # if start_control is false, then the air conditioner should be control manually
        computer_control = host.check_start_control()
        # Timer is needed to for data collection and control action caculation
        timer = Timer()
        timer.start()
        last_step_missing_data = False
        while (host.power_state):
            # check whether the timer reaches to data_request_seconds
            if (timer.check() > host.data_request_seconds or first_action == True):
                if (first_action == True):
                    first_action = False
                # stop the timer for request_data
                timer.stop()
                # request new data
                host.send_new_data_requestion()
                # this Timer is used to notice the user the device has errors.
                data_request_timer = Timer()
                data_request_timer.start()
                missing_data = False
                while (not host.check_has_new_data()):
                    if (data_request_timer.check() > 10):
                        missing_data = True
                        break
                # collect data first
                data_pkg = host.collect_data()

                if (host.current_step % host.period == 0 or last_step_missing_data == True):
                    if (missing_data == True):
                        last_step_missing_data = True
                    else:
                        last_step_missing_data = False
                        # ensure that it is not set to manual control
                        if (computer_control == True):
                            pass


if (__name__ == "__main__"):
    data_pkg =   {
       "body": 31.524999619,
       "feedback": "A Bit Hot",
       "hum": 58.200000763,
       "light": 38.333332062,
       "move_type": "work",
       "outdoor_des": "overcast clouds",
       "outdoor_hum": 41,
       "outdoor_press": 101.3,
       "outdoor_temp": 24.74000000000001,
       "press": 101.300003052,
       "set_fanspeed": 1,
       "set_temp": 18,
       "stepNo": 0,
       "temp": 26.399999619,
       "time": "2020-04-15 17:28:45.172778"
    }
    model = supervised_model.create_model()
    model.load_model()
    np.set_printoptions(suppress=True,edgeitems=10,linewidth=200)
    history_data = get_all_data()
    history_norm = np.copy(np.linalg.norm(history_data[:,0:7], axis=1))
    control_algorithm(model, data_pkg, history_data, history_norm)


