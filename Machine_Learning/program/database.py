import realtime_firebase as rt_fb
import cloud_firestore as c_fs


class Database:

    def __init__(self):
        self.realtime_db = rt_fb.Realtime_firebase()
        self.cloud_db = c_fs.Cloud_firestore()
        self.username = ""
        self.smartwatch_id = ""
        self.acmonitor_id = ""


    # set up target username
    def set_user(self, username):
        user_search_path = "Users/"+username;
        if (self.cloud_db.check_path(user_search_path)):
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
            return True
        else:
            print("Setup Terminate! User is not setup yet!")
            return False



db = Database()
db.set_user('eddylau')
db.setup()

