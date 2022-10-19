import time
import datetime
from model import RTSP
from model.SessionManager import _SessionManager
from definitions import Globals, DefObjects
from definitions.DefObjects import PlayoutModeEnum
from model.RTSP import GlobalCseq, SessionStateEnum, RTSPStatusCodeEnum
from model.RTSP.NGODSession import NGODSession
from model.RTSP.RtspRollingBuffer import RtspRollingBuffer
from model.RTSP.ShawSession import ShawSession

class RtspSessionManager(_SessionManager):
    def __init__(self, networkService,sendingThread):
        super(RtspSessionManager, self).__init__(networkService,sendingThread)
        self.Cseq = GlobalCseq()

    def parse_asset(self, asset_line):
        asset_name,start,end = asset_line.split()
        if(end == "-1"):
            asset_duration = float(
                int(Globals.managerObj.get_asset_duration(asset_name)) - int(start))
        else:
            asset_duration = float(int(end) - int(start))
        self.assets.append(DefObjects.Asset(asset_name,start,end,asset_duration))





    def AddSession(self, stb_addr = None ):
        _SessionManager.AddSession(self, stb_addr )
        if(stb_addr == None):
            stb_addr = self.ips.get_next()

        if Globals.cfg.playout_mode ==  PlayoutModeEnum.NGOD:
            session = NGODSession(self.assets_iter.next(),stb_addr,self.GlobalCseq,self.streamer_iter.next(),self.sessionIdCount,self.sendingThread,self.scheduler)
        elif Globals.cfg.playout_mode ==  PlayoutModeEnum.RTSP:
            session = ShawSession(self.assets_iter.next(),stb_addr,self.GlobalCseq,self.streamer_iter.next(),self.sessionIdCount,self.sendingThread,self.scheduler)
        elif Globals.cfg.playout_mode ==  PlayoutModeEnum.ROLLINGBUFFER:
            session = RtspRollingBuffer(self.assets_iter.next(),stb_addr,self.GlobalCseq,self.streamer_iter.next(),self.sessionIdCount,self.sendingThread,self.scheduler)
        self.HandleQ.put(session)
        self.SessionList.append(session)
        self.networkService.Register(session)






    def handleSessionState(self,session):
        try:
            _SessionManager.handleSessionState(self,session)
            if(session.state == SessionStateEnum.INIT):
                #if session in init state start the session to start the workflow
                #for some session describe and others setup
                #TODO: set the start method in all session types
                session.start()


            elif(session.state == SessionStateEnum.DESCRIBE_RECEIVED):
                session.allocate()

            elif(session.state == SessionStateEnum.SETUP_RECEIVED):
                session.doPlay()
                self.scheduler.addNewTask(time.time() +datetime.timedelta(seconds=session.duration).seconds,self.closeSession,session)


            elif(session.state == SessionStateEnum.TEARDOWN_RECEIVED):
                session.reset_url()
                session.state = SessionStateEnum.INIT
                self.HandleQ.put(session)

        except Exception,e:
            self.session_manager_log.error("Houston, we have a major problem %s in handleSessionState", e, exc_info=1)






    def __handle_redirect__(self,msg,session):
        session.state+=1
        if("Location" in msg.headers):
            self.networkService.UnRegister(session)
            session.handleRedirect(msg.headers["Location"])
            self.HandleQ.put(session)

        else:
            print "error got redirect but no location found"


    def handleReceived(self,session,msg):
        try:
            try:
                if(RTSP.is_rtsp_response(msg)):
                    messages = RTSP.parse_massages(msg)

                else:
                    return
            except Exception ,x:
                if(RTSP.is_rtsp_response(msg)):
                    print "Still unable to parse"
                    session.state +=1
                return -1

            for msg in messages:
                if(msg.code == 200 or msg.code == 302):
                    session.session_log.debug(msg)
                else:
                    session.session_log.error(msg)
                if(Globals.cfg.single_connection):
                    session = self.Cseq.GetSession(int(msg.headers["CSeq"]))
                if(msg.code == RTSPStatusCodeEnum.MOVED_TEMPORARILY or msg.code == RTSPStatusCodeEnum.MOVED_PERMANENTLY):
                    self.__handle_redirect__(msg,session)
                    continue
                if(session.state == SessionStateEnum.DESCRIBE_SENT):
                    session.state +=1
                    if(not session.handle_DESCRIBE_reply(msg)):
                        print "Error DESCRIBE response contains no header - a=control:"
                        self.ErrorSessionsQueue._put(session)
                        continue
                    self.HandleQ.put(session)

                elif (session.state == SessionStateEnum.SETUP_SENT):
                    session.state +=1
                    if(not session.handle_SETUP_reply(msg)):
                        print "Error SETUP response contains no header - Session"
                        self.ErrorSessionsQueue._put(session)
                        continue
                    self.HandleQ.put(session)

                elif (session.state == SessionStateEnum.PLAY_SENT):
                    session.state +=1
                    session.handle_PLAY_reply(msg)

                elif (session.state == SessionStateEnum.PAUSE_SENT):
                    session.state +=1
                    session.handle_PAUSE_reply(msg)

                elif (session.state == SessionStateEnum.GET_PARAMETERS_SENT):
                    session.state +=1
                    session.handle_GETPARAMS_reply(msg)


                elif (session.state == SessionStateEnum.TEARDOWN_SENT):
                    session.state+=1
                    self.HandleQ.put(session)

        except Exception,e:
            self.session_manager_log.error("Houston, we have a major problem %s in handleReceived", e, exc_info=1)


