from libs.timer import Timer
from libs import ac_host
import supervised_learning as supervised_model
import datetime
import random
import sys
import argparse


if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument("--random", default=True, help="Generate sample data for training")
    parser.add_argument("--predict",default=None, help="Control air conditioner by prediction")
    args = parser.parse_args()
    is_predict = False
    filepath = ""
    host = ac_host.AC_host("fyp0001","watch0001")
    if (args.random == True and args.predict == None):
        print("Initiate Data Collection Process [Y/n]?  ", end="")
        is_predict = False
    elif (args.predict != None):
        print("Input Thermal Comfort Prediction Model : <{}>".format(args.predict))
        filepath = 'trained_models_output_7/'+args.predict
        try:
            with open(filepath, 'r') as file:
                print("filepath <{}> is exist".format(filepath))
                # Do something with the file
        except IOError:
            print("filepath <{}> is not exist".format(filepath))
            sys.exit()
        print("Initiate Thermal Comfort Prediction Process [Y/n]?  ", end="")
        is_predict = True
    else:
        sys.exit()

    decision = input()
    while(decision is not 'y' and decision is not 'Y' and decision is not 'n'):
        decision = input()

    overall_timer = Timer()
    overall_timer.start()
    if (decision == "y" or decision == "Y"):
        if (is_predict):
            model = supervised_model.create_model()
            model.load_model(filepath)
        # if the AC is not yet TURN ON => TURN ON
        # else do nothing

        if (host.power_state is False):
            if (host.check_action_done()):
                host.ac_power_switch(True)
            print("Waiting AC Remote respoonse")
            while(not host.check_action_done()):
                pass
            host.update_ac_status()
            print("AC is switched ON")

        # Initiating the random action command
        data_request_timer = Timer()
        data_request_timer.start()
        host.set_is_learning(True)
        while(host.power_state):
            if (data_request_timer.check() > host.data_request_period):
                host.send_new_data_requestion()
                data_request_timer.stop()
                while (not host.check_has_new_data()):
                    pass

                data_pkg = host.collect_data()
                if (host.current_step % host.period == 0):
                    is_pass = False
                    if (host.check_override_control()):
                        control_pair = host.get_override_control_setting()
                        host.set_override_control(False)
                    else:
                        if (is_predict):
                            sorted_list, prob_comfy = model.predict(data_pkg)
                            index = 0
                            for i in range(1, len(prob_comfy)):
                                if ((abs(prob_comfy[0])-abs(prob_comfy[i]))*100 > 5.0):
                                    index = i-1
                                    break
                            if (index > 5):
                                print("Top {} actions, with selected top {}:".format(index,index))
                                for i in range(index):
                                    print("Temp: {}, Fanspeed: {}, Comfy Probability: {:.2f}".format(
                                        sorted_list[i][0]+17,sorted_list[i][1]+1,prob_comfy[i]*100))
                            else:
                                print("Top 5 actions, with selected top {}:".format(index))
                                for i in range(5):
                                    print("Temp: {}, Fanspeed: {}, Comfy Probability: {:.2f}".format(
                                        sorted_list[i][0]+17,sorted_list[i][1]+1,prob_comfy[i]*100))
                            # epsilon to choose the best action
                            if (random.random() > 0.5):
                                index = 0
                            # choose a random action
                            else:
                                if (index != 0):
                                    index = random.randint(1, index)
                            print("selection: {}".format((sorted_list[index][0]+17,sorted_list[index][1]+1)))
                            if (sorted_list[index][0]+17 == host.set_temperature and sorted_list[index][1]+1 == host.set_fanspeed):
                                is_pass = True
                            else:
                                is_pass = False
                            control_pair = host.generate_control_pair(input_temp=sorted_list[index][0], input_fanspeed=sorted_list[index][1])
                        else:
                            control_pair = host.generate_control_pair()
                    if (is_pass == False):
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

                data_request_timer.start()
                host.push_data(data_pkg)
                print(f'Step: {host.current_step+1} {data_pkg}')
                host.current_step += 1
                host.update_step_no()

                if (host.get_is_learning() is False):
                    if (host.check_action_done()):
                        host.ac_power_switch(False)
                    print("Waiting AC Remote respoonse")
                    while(not host.check_action_done()):
                        pass
                    host.update_ac_status()
                    print("AC is switched OFF")


    print(f"Section has {host.current_step} steps.", end=" ")
    overall_timer.stop(show=True)




'''
host.generate_control_pair()
print(host.read_action_done())
currentDT = datetime.datetime.now()
print (str(currentDT))
print(host.check_has_new_data())
'''
