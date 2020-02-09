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


    def getLatestData(self):
        try:
            ref = db.reference('sensor')
            # forming a list of data
            data = [detail for _ , detail in ref.get().items()]
            # get the latest data from the list
            return data.pop()
        except:
            print("Failed to get the latest data ...")
            return


    def sendAction(self, action):
        try:
            ref = db.reference('step')
            ref.push({'action':action})
            print("Action %s has been sent successful" %action)
        except:
            print("Action %s sending failed" %action)


    def __del__(self):
        print("Disconnected to realtime firebase ...")
