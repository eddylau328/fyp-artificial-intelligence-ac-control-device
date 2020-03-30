from libs import realtime_firebase as rt


if (__name__ == "__main__"):
    database = rt.Realtime_firebase()
    database.extract_data('Devices/fyp0001/datapack', show=True, export=True, dataname='datapack', filename='env_train_data')

