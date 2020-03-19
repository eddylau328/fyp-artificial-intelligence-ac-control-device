import firebase_admin
from firebase_admin import credentials, firestore


class Cloud_firestore:

    def __init__(self):
        try:
            # Fetch the service account key JSON file contents
            cred = credentials.Certificate('../../../fypacmonitor-firebase-adminsdk-s80u2-878cd05541.json')
            cloud_app = firebase_admin.initialize_app(cred, {
              'projectId': 'fypacmonitor',
            })
            self.cloud_db = firestore.client()
            print("Connected to firestore cloud ...")
        except:
            print("Failed to connect to firestore cloud ...")


    def add(self, path, data):
        try:
            doc_ref = self.cloud_db.document(path)
            doc_ref.set(data)
            print("Added %s data to firestore cloud" %path)
            return True
        except:
            print("Failed to add %s data to firestore cloud" %path)
            return False


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
            print('No such document!')
            return


    def check_document(self, path):
        doc_ref = self.cloud_db.document(path)
        doc = doc_ref.get()
        if doc.exists:
            return True
        else:
            return False


    def move(self, original_path, new_path):
        # original_path needs to exist, new_path needs to not exist
        if (self.check_document(original_path) and not self.check_document(new_path)):
            data = self.get(original_path)
            isSuccess = self.add(new_path, data)
            # prevent add data process fail, lossing all the data
            if (isSuccess == True):
                self.delete(original_path)
            else:
                print("Fail, terminate move document process!")
                return False
            return True
        else:
            return False


    def delete(self, path):
        doc_ref = self.cloud_db.document(path)
        try:
            doc_ref.delete()
            print('Success to delete document %s!' %path)
            return True
        except:
            print('Fail to delete document %s!' %path)
            return False


    def __del__(self):
        print("Disconnected to firestore cloud ...")


