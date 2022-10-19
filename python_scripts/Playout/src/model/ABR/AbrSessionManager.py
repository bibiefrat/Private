import os
import random
import time
import datetime
import itertools
from ConfigReader import cfg
from definitions import Globals
#from definitions.Logger import timeit
from model.ABR import AbrSessionStateEnum, AbrAsset, AbrSessionProfile, percentage,   AssetList,  get_rolling_buffers_as_assets, CriticalErr
from model.ABR.HlsSession import HlsSession
from model.ABR.HttpSessionManager import _HttpSessionManager
from model.ABR.SmoothSession import SmoothSession
from model.SessionManager import _SessionManager

class AbrSessionManager(_HttpSessionManager):




    def update_rolling_buffer_asset_list(self):
        dump = open("../conf/AbrAutoList.txt", mode="w+")

        self.assets.extend(get_rolling_buffers_as_assets())
        dump.writelines([str(x) + "\n" for x in self.assets])
        dump.close()
        self.scheduler.addNewTask(time.time() + datetime.timedelta(minutes=cfg.buffer_sampling_interval).seconds,self.update_rolling_buffer_asset_list)

    def __init__(self, networkService, sendingThread):
        super(AbrSessionManager, self).__init__(networkService, sendingThread)
        self.streamers = []
        if(cfg.streamer_ip=="0"):
            self.streamers = Globals.managerObj.DiscoverTopology()
        else:
            for streamerIp in cfg.streamer_ip.split(","):
                self.streamers.append(streamerIp)

        self.streamers_iter = itertools.cycle(self.streamers)
        self.sessions_to_change_level = percentage(cfg.sessions_change_level_percent,cfg.total_sessions)
        self.buffer_list = {}
        if(cfg.slice_buffer == 1):
            self.assets = AssetList()
            self.update_rolling_buffer_asset_list()
            self.assets_iter = itertools.cycle(self.assets)

        #statistics
        self.manifest_max = 0
        self.manifest_min = 0
        self.manifest_avg = 0








    def parse_asset(self, asset_line):
        if(cfg.slice_buffer != 1):
            asset_name,start,end = asset_line.split()
            asset = AbrAsset(asset_name,start,end)
            self.assets.append(asset)
            self.session_manager_log.devel("successfully parsed asset :" +str(asset))

#    @timeit
    def AddSession(self,stb_addr=None):
        _SessionManager.AddSession(self, None )
        if(cfg.abr_session_type == AbrSessionProfile.HLS):
            session = HlsSession(self.assets_iter.next(), None, self.streamers_iter.next(), self.sessionIdCount,self.sendingThread,self.scheduler)
        elif (cfg.abr_session_type == AbrSessionProfile.SMOOTH):
            session = SmoothSession(self.assets_iter.next(), None, self.streamers_iter.next(), self.sessionIdCount,self.sendingThread,self.scheduler)
        #
        self.SessionList.append(session)
        self.networkService.Register(session)
        self.HandleQ.put(session)


#    @timeit
    def handleSessionState(self, session):
        if(session.state == AbrSessionStateEnum.INIT):
            session.start()
            if(self.sessions_to_change_level>0):
                self.scheduler.addNewTask(time.time() + datetime.timedelta(seconds=random.randint(30,session.duration -10)).seconds,session.change_level)
                self.sessions_to_change_level-=1
        elif(session.state == AbrSessionStateEnum.CLOSED):
            self.session_manager_log.debug("Closing session " + str(session.private_ID))
            self.networkService.UnRegister(session)
            self.closeSession(session)
            self.remove_session(session)
	    if(not cfg.manifets_only):
                self.scheduler.addNewTask(time.time(),self.AddSession,session.stb_addr)

        _HttpSessionManager.handleSessionState(self,session)

#    def handleSessionState(self, session):
#        super(AbrSessionManager, self).handleSessionState(session)
#    @timeit
    def handleHttpMsg(self, session, msg, content=None):
        try:
            super(AbrSessionManager, self).handleHttpMsg(session, msg, content)
            if(session.state == AbrSessionStateEnum.MANIFEST_REQUEST_RECEIVED):
                if(int(cfg.manifest_only) != 1):
                    session.handle_manifest_response(content)
                    session.request_fregments_list()
                else:
                    session.state = AbrSessionStateEnum.CLOSED
                    session.manifest_request_time = time.time() -  session.manifest_request_time
                    if(self.manifest_min == 0):
                        self.manifest_min = session.manifest_request_time
                    if(self.manifest_avg == 0):
                        self.manifest_avg = session.manifest_request_time



                    if(session.manifest_request_time >self.manifest_max):
                        self.manifest_max = session.manifest_request_time
                    elif(session.manifest_request_time <self.manifest_min):
                        self.manifest_min = session.manifest_request_time
                    if(self.manifest_min == 0):
                        self.manifest_min = session.manifest_request_time
                        self.manifest_avg = session.manifest_request_time

                    self.manifest_avg = (self.manifest_avg +  session.manifest_request_time) /2

                    self.session_manager_log.info("\n"+'*'*100 + "\n\tmanifest statistics:\n\tmin : " +  str(self.manifest_min) + "max : " + str(self.manifest_max) + " avg : " + str(self.manifest_avg)+"\n"+'*'*100 )

            elif (session.state == AbrSessionStateEnum.FRAGMENT_LIST_REQUEST_RECEIVED):
                session.handle_fragment_list_response(content)


            elif (session.state == AbrSessionStateEnum.MANAGER_MANIFEST_REQUEST_RECEIVED):
                session.handle_manager_response(content)
                self.networkService.UnRegister(session)
                session.request_manifest()
        except CriticalErr,x:
            self.session_manager_log.exception(x)
            if(cfg.sys_exit_on_critical==1):
                os._exit(1)
            else:
                session.state = AbrSessionStateEnum.CLOSED


    def handle_fragment_response(self, session):
#        print str(session.session_id) + " done fragment"
        session.handle_fragment_response()

    def __handle_fragment_start__(self, session, fragment_headers, raw_data):
        session.state+=1
        super(AbrSessionManager, self).__handle_fragment_start__(session, fragment_headers, raw_data)
        session.handle_fragment_start()


#    def __handle_fragment_data__(self, session, raw_data):
#        pass
#




