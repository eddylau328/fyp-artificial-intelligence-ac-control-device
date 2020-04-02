from libs import realtime_firebase as rt


if (__name__ == "__main__"):
    database = rt.Realtime_firebase()
    data = database.extract_data('Devices/fyp0001/datapack', get=True)
    pack = []
    for i in range(len(data)):
        if (data[i]['stepNo'] == 0):
            pack.append(i)
    print(pack)
    new_data = []
    for i in range(pack.pop(), len(data)):
        new_data.append(data[i])
    database.export(data=new_data,dataname='datapack',filename='env_training_data/env_data_7')
