import Queue
import logging

import threading
import time
import sys
import itertools
from ConfigReader import cfg

from definitions import Globals
import model

from model.RTSP import GlobalCseq
from model.Scheduler import Scheduler


class _SessionManager(threading.Thread):
    def __init__(self,networkService,sendingThread):
        super(_SessionManager, self).__init__()
        self.session_manager_log = logging.getLogger(type(self).__name__ )

        self.networkService = networkService
        self.sendingThread = sendingThread
        self.HandleQ = Queue.Queue()

        self.realIPs = cfg.real_stb.split(';')

        if(cfg.streamer_id!=0):
            self.streamer = str(cfg.streamer_id).split(';')
        else:
            self.streamer = "0"

        self.fake_stbs = [model.ipAddr_iter(x,cfg.init_port,cfg.one_fake_machine == 1) for x in cfg.fake_stb.split(';')]

        self.realIPs_iter = iter(self.realIPs)
        self.streamer_iter = itertools.cycle(self.streamer)
        self.fake_stbs_iter = itertools.cycle(self.fake_stbs)

        self.ips = model.ipAddr_distrib(cfg.real_session,self.realIPs_iter,self.fake_stbs_iter)

        self.ErrorSessionsQueue = Queue.Queue()
        self.SessionList = []
        self.running = True
        self.sessionIdCount = 0
        self.scheduler = Scheduler()
        self.scheduler.start()
        self.assets = []
        self.ReadAssetList()
        self.assets_iter = itertools.cycle(self.assets)
        self.session_open_delay =  1.0/cfg.sessions_per_second
        self.GlobalCseq = GlobalCseq()

    def parse_asset(self,asset_line):
        raise NotImplementedError

    def ReadAssetList(self):
        try:
            asset_file = open(cfg.asset_list_path, "r")
        except IOError:
            print self.session_manager_log.critical("asset list file cannot be found at " + cfg.asset_list_path)
            sys.exit(0)
        all_lines = asset_file.readlines()
        for line in all_lines:
            if(not line.startswith("#") and line.strip()!=""):
                self.parse_asset(line)
        asset_file.close()


    def AddSession(self,stb_addr = None):
        self.sessionIdCount+=1
        time.sleep(self.session_open_delay)


    def remove_session(self, session):

        if(session in self.SessionList):
            self.SessionList.remove(session)
        else:
            self.session_manager_log.critical("unable to remove session from sessionlist")


    def run(self):
        while(self.running):
            try:
                Msg = self.networkService.getNextMsg()
                while(Msg!=None):
                    session,message =Msg
                    self.handleReceived(session,message)
                    Msg = self.networkService.getNextMsg()
    #            self.session_list_lock.acquire()
                while(not self.HandleQ.empty()):
                    session =self.HandleQ.get()
                    self.handleSessionState(session)
    #            for session in self.SessionList:
    #                self.handleSessionState(session)
    #            self.session_list_lock.release()
            except :
                time.sleep(0.001)

    def closeSession(self,session):
        if(session.active):
            session.end()
            session.cleanUp()


    def handleSessionState(self,session):

        if(session.isPlaying() and not session.inTrickPlay and cfg.trick_play_percent>0):
            currentTime = time.time()
#            self.session_manager_log.devel("getting tp command for session "  + session.session_id)
            tp_command = Globals.trickplay_mixer.get_command()
            if(tp_command!=None):
#                self.session_manager_log.devel("**session: "+session.session_id+" - handleSessionState - tp_command issue")
                session.do_trickplay(currentTime,tp_command)

    def handleReceived(self,session,msg):
        raise NotImplementedError



if __name__=="main":
    pass


