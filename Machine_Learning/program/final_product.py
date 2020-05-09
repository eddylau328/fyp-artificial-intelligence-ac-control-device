from libs.ac_host import AC_host
from libs.timer import Timer
from datetime import datetime
import supervised_learning as supervised_model
import json
import numpy as np
import pandas as pd
import copy

# similarity accept top 5 choices, With larger numbers the accuracy of the future points will decrease
SIMILARITY_ACCEPT = 100
# exploration epsilon that it will select an unknown future action or a known future action
# with more data this number should decrease, and if all the actions are known, it will automatically go to do known action
EXPLORATION_EPSILON = 0.8
# with unknown actions, it could choose to do the action
# whether it could get maximum value of first probability or random choose an action
UNKNOWN_EXPLORATION_EPSILON = 0.7
# with exploration action, it could choose to do the action
# whether it could get maximum value from the weight equation or random choose an action to explore the future feedback
# as the delta time is also counted in the future caculation
KNOWN_EXPLORATION_EPSILON = 0.7
# this is used in the overall probability equation, P = P_i * (1-w_f) + P_f * w_f
FUTURE_WEIGHTS = 0.4
# this is used in checking the
#MAX_DELTA_TIME = 60 * 10

DATA_REQUEST_SECONDS = 60
STEP_CALCULATION_PERIOD = 15

DATA_NORM_PARA = []

def normalize_data(x, method, given_constants=None):
    if (method == "max_min" and given_constants == None):
        max, min = x[:].max(), x[:].min()
        #print(max, min)
        x[:] = (x[:]-min)/(max-min)
        return x, max, min
    elif(method == "mean_std" and given_constants == None):
        mean, std = np.mean(x[:]), np.std(x[:])
        x[:] = (x[:]-mean)/std
        return x, mean, std
    elif(method == "max_min"):
        max, min = given_constants[0], given_constants[1]
        if (len(x.shape) == 0):
            x = (x-min)/(max-min)
        else:
            x[:] = (x[:]-min)/(max-min)
        return x
    elif(method == "mean_std"):
        mean, std = given_constants[0], given_constants[1]
        if (len(x.shape) == 0):
            x = (x-mean)/std
        else:
            x[:] = (x[:]-mean)/std
        return x
    else:
        return


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


def get_future_point(environment_data, history, history_normalize, norms, action_list):
    input_vector = np.array([environment_data['temp'],environment_data['hum'],environment_data['outdoor_temp'],environment_data['outdoor_hum'],environment_data['body']])
    normalize_input_vector = np.copy(input_vector)
    for i in range(4):
        normalize_input_vector[i] = normalize_data(normalize_input_vector[i], method="max_min", given_constants=DATA_NORM_PARA[i])
    similarity_list = cosine_similarity(history_normalize[:,0:4],normalize_input_vector[0:4], norms)
    sorted_index = similarity_list.argsort()[::-1]
    extract_data = np.zeros((SIMILARITY_ACCEPT,9))
    extract_data[:,0:8] = np.copy(history[sorted_index][:SIMILARITY_ACCEPT])
    extract_data[:,8] = np.copy(sorted_index[:SIMILARITY_ACCEPT])

    future_point_list = []

    for j in range(action_list.shape[0]):
        filter_data = np.copy(extract_data[extract_data[:,5] == action_list[j][0]])
        filter_data = np.copy(filter_data[filter_data[:,6] == action_list[j][1]])
        #print(filter_data)
        if (filter_data.size == 0):
            #print("no similar point found")
            future_point_list.append([0, 0, 0, 0, 0])
        else:
            normalize_filter_data = np.copy(filter_data)
            for i in range(4):
                normalize_filter_data[:,i] = normalize_data(normalize_filter_data[:,i], method="max_min", given_constants=DATA_NORM_PARA[i])
            similarity_list = cosine_similarity(normalize_filter_data[:,0:4], normalize_input_vector[0:4], np.linalg.norm(normalize_filter_data[:,0:5], axis=1))
            sorted_index = similarity_list.argsort()[::-1]
            filter_data = np.copy(filter_data[sorted_index])
            temp_hum_pair = [0, 0, 0, 0, 0]
            #print("similar point = {}".format(filter_data[0]))
            # extract_data[0][8] is the index, extract_data[0][7] is delta time
            start_time = filter_data[0][7]
            temp_hum_pair[0], temp_hum_pair[1] = filter_data[0][0], filter_data[0][1]

            for i in range(int(filter_data[0][8]), history.shape[0]):
                if (history[i][5] == action_list[j][0] and history[i][6] == action_list[j][1]):
                    temp_hum_pair[2] = history[i][0]
                    temp_hum_pair[3] = history[i][1]
                    temp_hum_pair[4] += (history[i][7]-start_time)
                    start_time = history[i][7]
                    #print(history[i])
                else:
                    break
            #print(temp_hum_pair)
            future_point_list.append(temp_hum_pair)

    return future_point_list


def control_algorithm(thermal_comfort_model, data_pkg, history, history_normalize, norms):
    pkg = copy.deepcopy(data_pkg)
    current_state_list = np.array([[pkg['temp'], pkg['hum']
                                , pkg['outdoor_temp'], pkg['outdoor_hum'], pkg['body']
                                , 0, i%3+1] for i in range(27)])
    for i in range(9):
        for j in range(3):
            current_state_list[i*3+j][5] = 17+i
    #print()
    #print(current_state_list)
    #print()
    sorted_list, first_prob_comfy = thermal_comfort_model.predict(pkg)
    sorted_list, first_prob_comfy = np.array(sorted_list), np.array(first_prob_comfy)
    sorted_list[:,0], sorted_list[:,1] = sorted_list[:,0] + 17, sorted_list[:,1] + 1
    future_points = np.array(get_future_point(pkg, history, history_normalize, norms, sorted_list))
    future_points = np.array(future_points)
    future_feedback = np.zeros(first_prob_comfy.shape)
    for i in range(future_points.shape[0]):
        if (future_points[i][0] != 0 and future_points[i][1] != 0):
            pkg['temp'], pkg['hum'] = future_points[i][0], future_points[i][1]
            future_feedback[i] = thermal_comfort_model.predict(pkg, [sorted_list[i][0], sorted_list[i][1]])
        else:
            future_feedback[i] = -1.0
    #print(future_feedback)
    record_table = np.zeros((27,11))
    record_table[:,0:2] = sorted_list
    record_table[:,2:4] = current_state_list[:,0:2]
    record_table[:,4:9] = future_points
    record_table[:,9] = first_prob_comfy
    record_table[:,10] = future_feedback

    record_table_df = pd.DataFrame(record_table, columns=['Set_Temp','Set_Fanspeed','Intial_Temp','Intial Hum','Similar_Initial_Temp','Similar_Intial Hum','Final_Temp','Final_Hum','Delta_Time','First_Step_Prob','Second_Step_Prob'])
    print()
    print(record_table_df)
    print()
    unknown_action = np.copy(record_table[record_table[:,10] == -1.0])
    known_action = np.copy(record_table[record_table[:,10] != -1.0])
    # first check whether it needs to explore or not
    if (unknown_action.shape[0] != 0 and np.random.uniform(0.0,1.0) < EXPLORATION_EPSILON):
        if (np.random.uniform(0.0,1.0) < UNKNOWN_EXPLORATION_EPSILON):
            # random choose from the unknown action list
            unknown_action_index = np.random.randint(low=0, high=unknown_action.shape[0])
            # the 0:2 are the set_temp and set_fanspeed
            selected_action = np.copy(unknown_action[unknown_action_index][0:2])
        else:
            # select the best action from the unknown action list according to their first action probability
            unknown_action_index = np.argmax(unknown_action[:,9])
            selected_action = np.copy(unknown_action[unknown_action_index][0:2])
    else:
        if (np.random.uniform(0.0,1.0) < KNOWN_EXPLORATION_EPSILON):
            known_action_index = np.random.randint(low=0, high=known_action.shape[0])
            selected_action = np.copy(known_action[known_action_index][0:2])
        else:
            # according to the weight equation, P_i * w_i + P_f * w_f = P
            final_probability = known_action[:,9] * (1-FUTURE_WEIGHTS) + known_action[:,10] * FUTURE_WEIGHTS
            known_action_index = np.argmax(final_probability)
            selected_action = np.copy(known_action[known_action_index][0:2])
    print("selected_action = {}".format(selected_action))
    # return a python list [set_temp, set_fanspeed]
    return selected_action.astype(int).tolist()


def main():
    # every 60 seconds it will request a data => data_request_seconds
    # every 5 * 60 sec it will do an action => steps_calculation_period
    host = AC_host(ac_serial_num="fyp0001",watch_serial_num="watch0001",data_request_seconds = DATA_REQUEST_SECONDS, steps_calculation_period=STEP_CALCULATION_PERIOD)
    model = supervised_model.create_model()
    model.load_model()
    # if terminate program is true, then this program will be terminated
    # terminate_program could only be changed on the firebase database
    need_start_restart = False
    while (not host.check_terminate_program()):
        # history_data is in numpy array
        np.set_printoptions(suppress=True,edgeitems=10,linewidth=200)
        history_data = get_all_data()
        history_norm = np.copy(np.linalg.norm(history_data[:,0:4], axis=1))
        history_data_normalize = np.copy(history_data)
        for i in range(4):
            history_data_normalize[:,i], norm_1, norm_2 = normalize_data(history_data_normalize[:,i], method="max_min")
            DATA_NORM_PARA.append([norm_1,norm_2])
        history_norm = np.copy(np.linalg.norm(history_data_normalize[:,0:4], axis=1))
        # reset the host program
        host.reset()
        # this is used to do action at the first time
        first_action = True

        if (need_start_restart == True):
            restart_timer = Timer()
            restart_timer.start()
            while (restart_timer.check() < 15):
                pass
            restart_timer.stop()
            need_start_restart = False
            host.set_override_control_setting(override_power=True)
            host.set_override_control(True)

        # if start ac is true, then the air conditioner should be turn on
        # start_ac is a button for the user to start the air conditioner on the mobile app
        print("Waiting User start AC")
        user_start_AC = False
        while (not user_start_AC):
            if (host.check_override_control()):
                control_pair = host.get_override_control_setting()
                user_start_AC = control_pair['power']

        host.set_override_control(False)

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
        # this Timer is used to notice the user the device has errors.
        data_request_timer = Timer()
        # this Timer() is used to check how long does the air conditioner switched on
        overall_timer = Timer()
        overall_timer.start()
        timer.start()
        override_last_step_missing_data = False
        while (host.power_state):
            # check whether the timer reaches to data_request_seconds
            if (timer.check() > host.data_request_seconds or first_action == True):
                # stop the timer for request_data
                timer.stop()
                # request new data
                host.send_new_data_requestion()
                data_request_timer.start()
                missing_data = False
                while (not host.check_has_new_data()):
                    if (data_request_timer.check() > 10):
                        missing_data = True
                        break
                data_request_timer.stop()
                # collect data first
                data_pkg = host.collect_data()


                # later delete
                if (host.current_step == 180):
                    host.push_data(data_pkg)
                    print(f'Step: {host.current_step+1} {data_pkg}')
                    host.current_step += 1
                    host.update_step_no()
                    if (host.check_action_done()):
                        host.ac_power_switch(False)
                    print("Waiting AC Remote response")
                    while(not host.check_action_done()):
                        pass
                    host.update_ac_status()
                    print("AC is switched OFF")
                    need_start_restart = True
                    break

                # check whether it needs to perform an action or not
                if (host.current_step % host.period == 0 or first_action == True):
                    if (first_action == True):
                        first_action = False
                    # if data is missing then the control action will be take place at next time
                    if (missing_data == False):
                        # ensure that it is not set to manual control
                        if (computer_control == True):
                            selected_action = control_algorithm(model, data_pkg, history_data, history_data_normalize, history_norm)
                            if (selected_action[0] == host.set_temperature and selected_action[1] == host.set_fanspeed):
                                isSameSettings = True
                            else:
                                isSameSettings = False
                            if (not isSameSettings):
                                # change the Numeric value to ENUM Class value
                                input_temp_class_value, input_fanspeed_class_value = selected_action[0]-17, selected_action[1]-1
                                control_pair = host.generate_control_pair(input_temp=input_temp_class_value, input_fanspeed=input_fanspeed_class_value)
                                command = host.generate_command('temp', control_pair['temp'])
                                host.send_control_command(command)
                                while (not host.check_action_done()):
                                    pass
                                command = host.generate_command('fanspeed', control_pair['fanspeed'])
                                host.send_control_command(command)
                                while (not host.check_action_done()):
                                    pass
                                host.update_ac_status()
                            host.update_period()
                            data_pkg['set_temp'], data_pkg['set_fanspeed'] = selected_action[0], selected_action[1]
                        # begin the data collection timer
                        timer.start()
                        host.push_data(data_pkg)
                        print(f'Step: {host.current_step+1} {data_pkg}')
                        host.current_step += 1
                        host.update_step_no()
                    else:
                        host.reset_data_request()
                        timer.start()
                else:
                    # if missing data then do not update steps, skip that period
                    if (missing_data == True):
                        host.reset_data_request()
                        timer.start()
                    else:
                        # begin the data collection timer
                        timer.start()
                        host.push_data(data_pkg)
                        print(f'Step: {host.current_step+1} {data_pkg}')
                        host.current_step += 1
                        host.update_step_no()

            # if user wants to correct the temperature or fanspeed by their own, then it allows them to do that
            # and the action the user performs will record as a step
            if (host.check_override_control() or override_last_step_missing_data):
                # request new data
                host.send_new_data_requestion()
                data_request_timer.start()
                missing_data = False
                while (not host.check_has_new_data()):
                    if (data_request_timer.check() > 10):
                        missing_data = True
                        break
                data_request_timer.stop()
                # collect data first
                if (missing_data == True):
                    override_last_step_missing_data = True
                else:
                    # stop the timer for request_data
                    timer.stop()
                    override_last_step_missing_data = False
                    data_pkg = host.collect_data()
                    control_pair = host.get_override_control_setting()
                    host.set_override_control(False)
                    if (control_pair['power'] == True):
                        command = host.generate_command('temp', control_pair['temp'])
                        host.send_control_command(command)
                        while (not host.check_action_done()):
                             pass
                        command = host.generate_command('fanspeed', control_pair['fanspeed'])
                        host.send_control_command(command)
                        while (not host.check_action_done()):
                            pass
                        host.update_ac_status()
                        data_pkg['set_temp'], data_pkg['set_fanspeed'] = control_pair['temp'], control_pair['fanspeed']
                        host.push_data(data_pkg)
                        print(f'Step: {host.current_step+1} {data_pkg}')
                        host.current_step += 1
                        host.update_step_no()
                        # begin the data collection timer
                        timer.start()
                    else:
                        host.update_ac_status()
                        data_pkg['set_temp'], data_pkg['set_fanspeed'] = control_pair['temp'], control_pair['fanspeed']
                        host.push_data(data_pkg)
                        print(f'Step: {host.current_step+1} {data_pkg}')
                        host.current_step += 1
                        host.update_step_no()
                        if (host.check_action_done()):
                            host.ac_power_switch(False)
                        print("Waiting AC Remote response")
                        while(not host.check_action_done()):
                            pass
                        host.update_ac_status()
                        print("AC is switched OFF")

        print(f"Section has {host.current_step} steps.", end=" ")
        overall_timer.stop(show=True)
        host.download_data()

if (__name__ == "__main__"):

    main()
    '''
    data_pkg = {
   "body": 35.306251526,
   "feedback": "acceptable",
   "hum": 57.400001526,
   "light": 0,
   "move_type": "sleep",
   "outdoor_des": "scattered clouds",
   "outdoor_hum": 78,
   "outdoor_press": 100.8,
   "outdoor_temp": 27.430000000000007,
   "press": 100.700004578,
   "set_fanspeed": 1,
   "set_temp": 19,
   "stepNo": 53,
   "temp": 22.899999619,
   "time": "2020-05-06 01:38:13.797437"
  }

    model = supervised_model.create_model()
    model.load_model()
    np.set_printoptions(suppress=True,edgeitems=10,linewidth=200)
    history_data = get_all_data()
    history_data_normalize = np.copy(history_data)
    for i in range(4):
        history_data_normalize[:,i], norm_1, norm_2 = normalize_data(history_data_normalize[:,i], method="max_min")
        DATA_NORM_PARA.append([norm_1,norm_2])
    history_norm = np.copy(np.linalg.norm(history_data_normalize[:,0:4], axis=1))
    control_algorithm(model, data_pkg, history_data, history_data_normalize, history_norm)
    '''

