import time
from definitions import Globals
from model.Session import Session

from model.RTSP import rtspVerbEnum, SessionStateEnum
from model.RTSP.RtspSession import RtspSession

class ShawSession(RtspSession):
    def __init__(self,assets,stb_addr,GlobalCseq,streamer_id,numSess,sendingThread,scheduler):
        RtspSession.__init__(self,assets,stb_addr,GlobalCseq,streamer_id,numSess,True,sendingThread,scheduler)

        self.streamer_id =  streamer_id
        if self.streamer_id == "0"  :
            self.streamer = "0.0.0.0"
        else:
            self.streamer = Globals.managerObj.get_streamer(self.streamer_id)

        self.headers["Transport"] = "MP2T/H2221/UDP;unicast;destination=003!%s!%s!%s;"\
                                    "bandwidth=%s" % (str(self.streamer), str(self.destinationIP), str(self.destinationPort),str(self.bitrate))
        self.headers["x-prepareAssets"] = ""
        self.headers["x-mayNotify"] = ""
        self.headers["Scale"] = "1.000"
        self.headers["Range"] = "npt=0-end"
        self.headers["Accept"] = "application/sdp"
        self.headers["Require"] = "x-mayNotify,x-noFlush,x-playNow"
        self.headers["x-noFlush"]= ""
        self.headers["x-playNow"] = ""
        self.headers["Content-Type"] = "text/parameters"

        self.setup_headers.extend(["Transport","x-prepareAssets","x-mayNotify","Scale","Range","Accept"])
        self.play_headers.extend(["x-playNow"])
        self.pause_headers.extend(["x-noFlush"])
        self.getparams_headers  =["CSeq","Session","Content-Type","Content-Length"]
        self.getparams_content = "position\r\nstream_state\r\nscale\r\n"
        self.next_tp_command = None

    def get_rtsp_url(self,command, selected_asset = None):
        if command == rtspVerbEnum.SETUP:
            return command +" rtsp://%s:554%s RTSP/1.0" % (str.strip(str(Globals.managerObj.manager_ip)), self.asset.id)            
        else:
            return command +" * RTSP/1.0"



    def do_trickplay(self,time,tp_command):
        self.session_log.debug("TP " + str(tp_command.scale))
        self.next_tp_command = tp_command
        self.rtsp_get_parameters()

    def handle_PLAY_reply(self,msg):
#       do not delete : this is to avoid entering trickplay by inheritance from rtspSession
        pass

    def handle_GETPARAMS_reply(self,msg):
        try:
            if(float(msg.headers["position"]) > self.duration):
                self.posision = self.duration
            else:
                self.posision = float(msg.headers["position"])

            if(int(self.next_tp_command.scale)>0):
                if(self.posision + int(self.next_tp_command.scale) >self.duration):
                    self.rtsp_seek(0+int(self.next_tp_command.scale))
                else:
                    self.rtsp_seek(self.posision+int(self.next_tp_command.scale))

            else:
                if(  self.posision +int(self.next_tp_command.scale) >0):
                    self.rtsp_seek(int(self.next_tp_command.scale) + self.posision)
                else:
                    self.rtsp_seek(0)


            Session.do_trickplay(self,time.time(),self.next_tp_command)
            self.scheduler.addNewTask(self.trick_exit_time,self.exitTrickPlay)
            self.next_tp_command = None


#
#            elif(int(self.next_tp_command.scale) + self.posision >self.duration):
#                self.rtsp_seek(-int(self.next_tp_command.scale) + (self.posision))
#            else:

        except Exception,x:
            print str(x)

    def exitTrickPlay(self):
        self.session_log.debug("exit TP " + str(self.currentScale))
        Session.exitTrickPlay(self)

    def rtsp_get_parameters(self):
        if(self.state<2):
            return
        if(self.session_id!=""):
            recv = self.handle_rtsp_request(rtspVerbEnum.GETPARAMS,self.getparams_headers,self.getparams_content)
            self.state = SessionStateEnum.GET_PARAMETERS_SENT
            return recv
        else:
            print "ERROR - Session has no session ID cannot send command GET_PARAMETER"

    def start (self):
         self.allocate()

    def rtsp_seek(self,s_npt):
        self.rtsp_play(str(s_npt),"end")
        return