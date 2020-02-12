import realtime_firebase as rt_fb
import cloud_firestore as c_fs
from enum import Enum

class DatabaseType(Enum):
    REALTIME = 1
    CLOUD = 2


class Database:

    def __init__(self):
        self.db = None
        self.username = ""
        self.smartwatch_id = ""
        self.acmonitor_id = ""
        self.is_set_up = False


    def connect_database(self, database_type):
        if (database_type == DatabaseType.REALTIME):
            self.db = rt_fb.Realtime_firebase()
        else:
            self.db = c_fs.Cloud_firestore()


    def disconnect_database(self):
        self.db.__del__()


    # set up target username
    def set_user(self, username):
        self.connect_database(DatabaseType.CLOUD)
        user_search_path = "Users/"+username+"/info/personal";
        if (self.db.check_document(user_search_path)):
            self.username = username
            print("Found user %s!" %username)
            return True
        else:
            print("Not Found user %s!" %username)
            return False


    def setup(self):
        if (self.username != ""):
            search_path = "Users/"+self.username+"/connect_device/smartwatch";
            # set the smartwatch id and the acmonitor id
            if (self.cloud_db.check_path(search_path)):
                self.smartwatch_id = self.cloud_db.get(search_path, keys=['id'])
                print("Detected smartwatch <%s> is connected to user <%s>!" %(self.smartwatch_id,self.username))
            else:
                print("Setup Terminate! Smartwatch cannot found!")
                return False
            search_path = "Users/"+self.username+"/connect_device/ACmonitor";
            if (self.cloud_db.check_path(search_path)):
                self.acmonitor_id = self.cloud_db.get(search_path, keys=['id'])
                print("Detected ac monitor <%s> is connected to user <%s>!" %(self.acmonitor_id,self.username))
            else:
                print("Setup Terminate! AC monitor cannot found!")
                return False
            self.is_set_up = True
            return True
        else:
            print("Setup Terminate! User is not setup yet!")
            return False


    def get_smartwatch_train_data(self, **kwargs):
        # prevent username is not setup
        if (not self.is_set_up):
            return

        search_paths = []
        if ('untrain' in kwargs):
            base_search_path = "Devices/"+self.smartwatch_id+"/train_dataset/untrain_dataset/"
        # work is the movement of working
        # For example, typing keyboard, writing
        if ('work' in kwargs):
            if (kwargs.get('work') == True):
                search_paths.append(base_search_path+"work")

        # move is the movement that describes user moving around the room but usually not that fast
        # For example, stretching, walking, grabbing things
        if ('move' in kwargs):
            if (kwargs.get('move') == True):
                search_paths.append(base_search_path+"move")

        # sleep is the movement that describes user sleeping
        # For example, laying down on the bed, turning around on the bed
        if ('sleep' in kwargs):
            if (kwargs.get('sleep') == True):
                search_paths.append(base_search_path+"sleep")

        if ('exercise' in kwargs):
            if (kwargs.get('exercise') == True):
                search_paths.append(base_search_path+"exercise")

        result_data = []

        for path in search_paths:
            if ('keys' in kwargs):
                result_data.append(self.cloud_db.get(path, kwargs.get('keys')))
            else:
                result_data.append(self.cloud_db.get(path))

        return result_data


    def cloud_move_data(self, original_path, new_path):
        # prevent username is not setup
        if (not self.is_set_up):
            return

        result = self.cloud_db.move(original_path, new_path)
        if (result):
            print("Success to move document from %s to %s!" %(original_path, new_path))
        else:
            print("Fail to move document from %s to %s!" %(original_path, new_path))


    #def transfer_realtime_data_2_cloud(self, realtime_db_path, cloud_path):



db = Database()
db.set_user('eddylau')
#db.setup()

#old = "Devices/" + db.smartwatch_id + "/train_dataset/untrain_dataset/work/test_move"
#new = "Devices/" + db.smartwatch_id + "/train_dataset/trained_dataset/work/test_move"
#db.cloud_move_data(old, new)

