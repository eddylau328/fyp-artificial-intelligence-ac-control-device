import firebase_admin
from firebase_admin import credentials, firestore


class Cloud_firestore:

    def __init__(self):
        try:
            # Fetch the service account key JSON file contents
            cred = credentials.Certificate('../../../fypacmonitor-firebase-adminsdk-s80u2-adb9132a09.json')
            cloud_app = firebase_admin.initialize_app(cred, name="cloud")
            self.cloud_db = firestore.client()
            print("Connected to firestore cloud ...")
        except:
            print("Failed to connect to firestore cloud ...")


    def addData(self,data_name, data):
        try:
            doc_ref = self.cloud_db.collection(u'record').document(data_name)
            doc_ref.set(data)
            print("Added %s data to firestore cloud" %data_name)
        except:
            print("Failed to add %s data to firestore cloud" %data_name)


    def __del__(self):
        print("Disconnected to firestore cloud ...")
