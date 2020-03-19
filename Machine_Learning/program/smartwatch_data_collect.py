from libs import realtime_firebase as rt


if (__name__ == '__main__'):
    r = rt.Realtime_firebase()
    move_type = input("Enter the movement type (move/rest/work/sleep):")
    if (move_type == "move" or move_type == "rest" or move_type == "work" or move_type == "sleep"):
        found = False
        i = 0
        filepath = ""
        while (not found):
            filepath = "smartwatch_data/"+move_type+"/"+move_type+"_acc_4hz_"+str(i)
            try:
                with open(filepath +'.json', 'r') as file:
                    i += 1
                    # Do something with the file
            except IOError:
                print("Data will be save to <%s>" %(filepath +'.json'))
                found = True

        answer = input("Proceed [y/n] ?")
        if (answer == 'y'):
            path = "Devices/watch0001/sensors"
            r.extract_data(path, export=True, dataname="acc", filename=filepath, delete=True)
    else:
        print("No such movement type!")
