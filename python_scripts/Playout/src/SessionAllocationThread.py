import threading
import time
from definitions import Globals

class Session_Allocation_Thread(threading.Thread):
    def __init__(self,Sessions_List,single_thread_socket,no_delay_sessions):
        threading.Thread.__init__(self)
        self.Sessions_List = Sessions_List
        self.no_delay_sessions = no_delay_sessions
        self.single_thread_socket = single_thread_socket
    def run(self):
        no_delay_session_count = self.no_delay_sessions
        for i in xrange(len(self.Sessions_List)):
        #            print "<<<<<<<<<<<<<<<<<<<<<<<<Alloc Session:>>>>>>>>>>>>>>>>>>>>>> " + str(self.Sessions_List[i].session_id)
            self.Sessions_List[i].allocate(self.single_thread_socket)
            if no_delay_session_count >= 1:
                no_delay_session_count -= 1
                continue
            else:
                time.sleep(Globals.cfg.sec_delay_sessions)
                no_delay_session_count = self.no_delay_sessions
