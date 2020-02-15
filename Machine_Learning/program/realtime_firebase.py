import firebase_admin
import json
import csv
from firebase_admin import credentials, db

class Realtime_firebase:

    def __init__(self):
        try:
            # Fetch the service account key JSON file contents
            cred = credentials.Certificate('../../../fypacmonitor-firebase-adminsdk-s80u2-878cd05541.json')
            # Initialize the app with a service account, granting admin privileges
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://fypacmonitor.firebaseio.com/'
            })
            print("Connected to realtime firebase ...")
        except:
            print("Failed to connect to Realtime firebase ...")


    # get data from the input path
    # **kwargs give condition
    def get(self, path):
        try:
            ref = db.reference(path)
            # forming a list of data
            data = [detail for _ , detail in ref.get().items()]
            return data
        except:
            print("Failed to get the data ...")
            return


    def check(self, path):
        try:
            ref = db.reference(path)
            if (ref.get().items() is not None):
                print("Path <%s> exists" %path)
                return True
            else:
                print("Path <%s> not exists" %path)
                return False
        except:
            print("Path <%s> not exists" %path)
            return False


    # add data to the input path
    def add(self, path, data):
        try:
            ref = db.reference(path)
            ref.push(data)
            print("Data has been sent successful")
        except:
            print("Data sending failed")


    def export(self, data, dataname, filename, indent=1):
        pack = {}
        pack[dataname] = data
        with open(filename+'.json', 'w') as outfile:
            json.dump(pack, outfile, indent=indent)
        print("Exported json file <%s>" %filename)


    # delete data to the input path
    def delete(self, path):
        try:
            ref = db.reference(path)
            ref.delete()
            print("Success removing data at <%s>" %path)
        except:
            print("Fail removing data at <%s>" %path)


    def extract_data(self, path, **kwargs):
        if (self.check(path)):
            data = self.get(path)
            if ('show' in kwargs):
                if (kwargs['show'] is True):
                    print(data)
            if ('export' in kwargs):
                if (kwargs['export'] is True):
                    self.export(data, kwargs.get('dataname', 'export'), kwargs.get('filename', 'output'), kwargs.get('indent', 1))
            if ('delete' in kwargs):
                if (kwargs['delete'] is True):
                    self.delete(path)
            if ('get' in kwargs):
                if (kwargs['get'] is True):
                    return data
        else:
            print("Fail to extract data")
            return


    def __del__(self):
        print("Disconnected to realtime firebase ...")
