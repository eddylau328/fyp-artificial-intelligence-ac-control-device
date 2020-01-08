import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class Realtime_firebase:

    def __init__(self):
        # Fetch the service account key JSON file contents
        cred = credentials.Certificate('../../../datalog-418c9-firebase-adminsdk-og0bw-bacec2a5fc.json')
        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://datalog-418c9.firebaseio.com/'
        })

    def getLatestData(self):
        ref = db.reference('sensor')
        # forming a list of data
        data = [detail for _ , detail in ref.get().items()]
        # get the latest data from the list
        return data.pop()

    def sendAction(self, action):
        ref = db.reference('step')
        ref.push({'action':action})

firebase = Realtime_firebase()
print(firebase.getLatestData())
firebase.sendAction(0)
