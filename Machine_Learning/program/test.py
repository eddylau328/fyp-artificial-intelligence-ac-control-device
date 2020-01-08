import realtime_firebase as rt_fb
import cloud_firestore as c_fs


class Database:

    def __init__(self):
        realtime_db = rt_fb.Realtime_firebase()
        cloud_db = c_fs.Cloud_firestore()
