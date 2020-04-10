from libs import realtime_firebase as rt


if (__name__ == "__main__"):
    database = rt.Realtime_firebase()
    data = database.extract_data('Devices/fyp0001/datapack', get=True)
    pack = []
    for i in range(len(data)):
        if (data[i]['stepNo'] == 0):
            pack.append(i)

    file_count = 1

    filepath = ""
    while (True):
        filepath = "env_training_data/env_data_"+str(file_count)
        try:
            with open(filepath +'.json', 'r') as file:
                file_count += 1
                # Do something with the file
        except IOError:
            file_count -= 1;

            break

    print("There are {} new data pack".format(len(pack)-file_count))

    print("Data will be save to:")

    for i in range(file_count+1, len(pack)+1):
        print("<env_training_data/env_data_" +str(i) + ".json>")


    answer = input("Proceed [y/n] ?  ")
    if (answer == 'y'):
        for j in range(len(pack), file_count, -1):
            new_data = []
            start = pack.pop()
            for i in range(start, len(data)):
                new_data.append(data[i])
            for i in range(start, len(data)):
                data.pop()
            filename = 'env_training_data/env_data_' + str(j)
            database.export(data=new_data,dataname='datapack',filename=filename)

