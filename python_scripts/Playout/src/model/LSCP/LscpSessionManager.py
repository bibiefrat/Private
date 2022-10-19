import urllib2
import time
import datetime

from model.SessionManager import _SessionManager
from definitions import Globals, DefObjects
from model.LSCP import LscpStateEnum, LSCP_Response, LSCP_status_enum, LSCP_Op_code_enum
from model.LSCP.LscpSession import LscpSession

class LscpSessionManager(_SessionManager):
    def __init__(self, networkService,sendingThread):
        super(LscpSessionManager, self).__init__(networkService,sendingThread)

    def parse_asset(self, asset_line):
        asset_name,start,end = asset_line.split()
        if(end == "-1"):
            asset_duration = float(
                int(Globals.managerObj.get_asset_duration(asset_name)) - int(start))
        else:
            asset_duration = float(int(end) - int(start))
        self.assets.append(DefObjects.Asset(asset_name,start,end,asset_duration))



    def AddSession(self, stb_addr=None ):
        _SessionManager.AddSession(self, stb_addr )
        if(stb_addr==None):
            stb_addr =  self.ips.get_next()

        session = LscpSession(self.assets_iter.next(),stb_addr,self.streamer_iter.next(),self.sessionIdCount,self.sendingThread,self.scheduler )
#        self.session_list_lock.acquire()
        self.SessionList.append(session)
#        self.session_list_lock.release()
        self.networkService.Register(session)
        self.HandleQ.put(session)

    def handleReceived(self,session,msg):
        if(isinstance(msg,urllib2.addinfourl)):
            if(session.state == LscpStateEnum.LSCP_ALLOCATE_START):
                session.handle_allocate_response(msg.read())
            elif (session.state == LscpStateEnum.LSCP_TRANSLATE_URL):
                session.handle_translate_response(msg.read())
                self.HandleQ.put(session)
            elif (session.state == LscpStateEnum.LSCP_EOS_START):

                self.scheduler.addNewTask(time.time(),self.AddSession,session.stb_addr)
#                del session
            return
        if(msg!=""):
            response = LSCP_Response(msg)
        else:
#            print "got no data"
            return


        session.current_npt = response.current_NPT
        if(response.status_code != LSCP_status_enum.LSCP_OK):
            self.session_manager_log.error(response)
            if(response.status_code == LSCP_status_enum.LSCP_BAD_START):
                print "eeee ? "
        else:

            self.session_manager_log.debug( "<<Session Number = " + str(session.session_id) + " " + str(response))


        if(response.op_code == LSCP_Op_code_enum.LSCP_PLAY_REPLY or response.op_code == LSCP_Op_code_enum.LSCP_RESUME_REPLY or response.op_code == LSCP_Op_code_enum.LSCP_PAUSE_REPLY):
            session.currentScale = response.scale
            if(response.scale == 0):
                session.state = LscpStateEnum.LSCP_PAUSE_RECEIVED
            else:
                session.state = LscpStateEnum.LSCP_PLAY_RECEIVED


        if(response.op_code == LSCP_Op_code_enum.LSCP_DONE):
            session.state = LscpStateEnum.LSCP_DONE_RECEIVED
            self.networkService.UnRegister(session)

        if(response.op_code == LSCP_Op_code_enum.LSCP_STATUS_REPLY):
            session.handle_status_response()




    def handleSessionState(self,session):

        if(session.state == LscpStateEnum.LSCP_INIT):
            session.allocate()
        elif(session.state == LscpStateEnum.LSCP_ALLOCATE_END):
            session.start()
            self.scheduler.addNewTask(time.time() +datetime.timedelta(seconds=session.duration).seconds,self.closeSession,session)
        elif(session.state == LscpStateEnum.LSCP_DONE_RECEIVED):
            self.closeSession(session)
            self.remove_session(session)

        _SessionManager.handleSessionState(self,session)


