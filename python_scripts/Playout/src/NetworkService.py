import Queue
import logging
import socket
import threading
import select
import time

#from definitions import Globals
import urllib2
import itertools

class NetworkService(threading.Thread):
    def __init__(self,recvBufferSize = 32768):
        threading.Thread.__init__(self)
        self.log = logging.getLogger("NetworkService")
        self.input = {}
        self._lock = threading.Lock()
        self.running = False
        self.MsgQueue = Queue.Queue()
        self.recvBufferSize = recvBufferSize


    def Register(self,session):
        if(session.connection_socket == None):
            self.log.devel("session has no fd on init - will get in on allocate ?")
            return
        self._lock.acquire()
        self.input[session.connection_socket] = session
        self._lock.release()


    def RegAllSessions(self,Sessions):
        if not self.running:
            for session in Sessions:
                self.input[session.connection_socket] = session
        else:
            exec Exception("error")


    def UnRegister(self,session):
        self._lock.acquire()
        if(self.input.has_key(session.connection_socket)):
            self.input.pop(session.connection_socket)
        else:
            self.log.log(5,"error key not found")
        self._lock.release()
        session.connection_socket.close()
        session.connection_socket = None

    def getMsgQueue(self):

        return self.MsgQueue

    def getNextMsg(self):
        if(self.MsgQueue.qsize()>0):
            return self.MsgQueue.get()
        else:
            return None

    def sample(self):

        self._lock.acquire()
        keys = self.input.keys()[:]
        self._lock.release()
        inputready,outputready,exceptready = select.select(keys,[],keys,0.3)

        return inputready,outputready,exceptready

    def run(self):
        self.running = True
        while self.running:
            try:
                inputready,outputready,exceptready = self.sample()

                for s in inputready:
                    data = s.recv(self.recvBufferSize)
                    if(data!=""):
                        self.MsgQueue.put((self.input[s],data))
                    if(self.MsgQueue.qsize()>10000):
                        print "this could go wrong !!! " + str(self.MsgQueue.qsize())

                for s in exceptready:
                    self.log.log(5,"connection lost " + str(s))
            except Exception,x:
#                self.log.error("error",x ,exc_info=1)
                time.sleep(0.01)
                pass


class SendingThreadPool(object):
    def __init__(self,networkService,number):
        self.sendingThreads = []
        for i in xrange(number):
            tmp = SendingThread(networkService)
            self.sendingThreads.append(tmp)
            tmp.start()

        self.threadIter = itertools.cycle(self.sendingThreads)

    def AddMsg(self,socket,msg):
        self.threadIter.next().AddMsg(socket,msg)

class SendingThread(threading.Thread):
    def __init__(self ,networkService):
        super(SendingThread, self).__init__()
        self.sendQueue = Queue.Queue()
        self.networkService = networkService
        self.running = True

    def AddMsg(self,socket,msg):
        self.sendQueue.put((socket,msg))

    def run(self):
        while(self.running):
            if (self.sendQueue.qsize()>0):
                for i in xrange(self.sendQueue.qsize()):
                    session,msg = self.sendQueue.get()
                    if(isinstance(msg,basestring)):
                        if(session.connection_socket==None):
                            session.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            session.connection_socket.connect((session.server,session.port))
                            self.networkService.Register(session)
                        try:
#                            print "sending " + msg
                            session.connection_socket.send(msg)
                        except :
                            session.session_log.error("socket disconnected !!!! (retry - reconnect)")
                            session.connection_socket = None
                            self.AddMsg(session,msg)
                    else:
                        response = urllib2.urlopen(msg)
                        self.networkService.getMsgQueue().put((session,response))




            else:
                time.sleep(0.01)



