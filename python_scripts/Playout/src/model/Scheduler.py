import logging
import threading

import time
import datetime
from model.Session import Session


def print_time(num,stringo):
    print num,stringo,str(datetime.datetime.now())

def print_time_1():
    print str(datetime.datetime.now())

class Scheduler(threading.Thread):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.tasks = {}
        self.log = logging.getLogger(type(self).__name__)
        self.running = True
#        self.dict_lock = threading.Lock()

    def addNewTask_noargs(self,time,task):
        self.log.debug("addNewTask_noargs q=" + str(len(self.tasks)))
        if(task == None):
            raise None
        if(not self.tasks.has_key(time)):
#            self.dict_lock.acquire()
            self.tasks[time] = task
#            self.dict_lock.release()
        else:
#            self.dict_lock.acquire()
            tmp = self.tasks[time]
            if(isinstance(tmp,list)):
                tmp.append(task)
            else:
                ap = []
                ap.append(tmp)
                ap.append(task)
                self.tasks[time] = ap
#            self.dict_lock.release()

    def addNewTask(self,time_to_ex,task,*args):
        self.log.devel("added task " + task.__name__)
        if(task.__name__  == "exitTrickPlay"):
            self.log.devel("addNewTask q=" + str(len(self.tasks)) + " " +task.__name__ +" session " +task.im_self.session_id+" - task id:" +str(id(task)) +" exit in " + str( time_to_ex -time.time()))

        if(task == None):
            raise Exception("")
        if(args == None):
            self.addNewTask_noargs(time_to_ex,task)


        if(not self.tasks.has_key(time_to_ex)):
#            self.dict_lock.acquire()
            self.tasks[time_to_ex] = (task,args)
#            self.dict_lock.release()
        else:
#            self.dict_lock.acquire()
            tmp = self.tasks[time_to_ex]
            if(isinstance(tmp,list)):
                tmp.append((task,args))
            else:
                ap = []
                ap.append(tmp)
                ap.append((task,args))
                self.tasks[time_to_ex] = ap
#            self.dict_lock.release()

    def get_top_task(self):
        try:
#            self.dict_lock.acquire()
            if(len(self.tasks)>0):
                return sorted(self.tasks.items())[0]
            else:
                return None
        finally:
            pass
#            self.dict_lock.release()


    def __call_task__(self,task,*args):
        self.log.devel("calling task " + str(task))
        if(isinstance(task.im_self,Session)):
            if(task.im_self.active):
                task.__call__(*args)
            else:
                self.log.warning("session not active")
        else:
            task.__call__(*args)

    def call_task(self,task):
        try:
#            print "calling task " + str(task)
            if(tuple(task)):
                self.__call_task__(task[0],*task[1])
            else:
                self.__call_task__(task[0],None)
        except Exception,e:
            self.log.exception(e)


    def call_task_list(self,tasks):
        for task in tasks:
            self.call_task(task)

    def run(self):
        while(self.running):
            current_time = time.time()
            top =  self.get_top_task()
            if(top):
                while(top!=None and current_time>=top[0]):
                    if(isinstance(top[1],list)):
                        self.call_task_list(top[1])
                    else:
                        self.call_task(top[1])
                    self.tasks.pop(top[0])
                    self.log.devel("done task q=" + str(len(self.tasks)))
                    top =  self.get_top_task()

            time.sleep(0.0001)





if __name__ == "__main__":

    p = Scheduler()
    p.start()
    print_time_1()
    five_sec = time.time() + datetime.timedelta(seconds=5).seconds
    ten_sec = five_sec + datetime.timedelta(seconds=5).seconds
    p.addNewTask(ten_sec,print_time,"1","aaa")
    p.addNewTask(ten_sec,print_time_1)
    p.addNewTask(five_sec,print_time,"2","bbb")
    p.addNewTask(five_sec,print_time,"3","ccc")
    p.addNewTask(five_sec,print_time,"4","ddd")
    p.addNewTask(ten_sec+ datetime.timedelta(seconds=5).seconds,print_time_1)


