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


    def add(self,data_name, data):
        try:
            doc_ref = self.cloud_db.collection(u'record').document(data_name)
            doc_ref.set(data)
            print("Added %s data to firestore cloud" %data_name)
        except:
            print("Failed to add %s data to firestore cloud" %data_name)


    def get(self, path, keys=None):
        doc_ref = self.cloud_db.document(path)
        try:
            doc = doc_ref.get()
            data = doc.to_dict()
            if (keys == None or keys == []):
                return data
            else:
                pack = {}
                if (len(keys) == 1):
                    if (keys[0] in data):
                        return data.get(keys[0])
                for key in keys:
                    if (key in data):
                        pack.set(key, data.get(key))
                return pack
        except:
            print(u'No such document!')
            return


    def check_path(self, path):
        doc_ref = self.cloud_db.document(path)
        try:
            doc = doc_ref.get()
            return True
        except:
            print(u'Path does not exist')
            return False


    def __del__(self):
        print("Disconnected to firestore cloud ...")
