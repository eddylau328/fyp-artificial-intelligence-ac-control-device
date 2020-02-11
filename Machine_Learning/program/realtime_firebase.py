import firebase_admin
from firebase_admin import credentials, db

class Realtime_firebase:

    def __init__(self):
        try:
            # Fetch the service account key JSON file contents
            cred = credentials.Certificate('../../../fypacmonitor-firebase-adminsdk-s80u2-adb9132a09.json')
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


    # add data to the input path
    def add(self, path, data):
        try:
            ref = db.reference(path)
            ref.push(data)
            print("Data has been sent successful")
        except:
            print("Data sending failed")


    def __del__(self):
        print("Disconnected to realtime firebase ...")

'''
    # delete data to the input path
    def delete(self, path, data=None):
        try:

        except:
            print("Data removing failed")
'''
