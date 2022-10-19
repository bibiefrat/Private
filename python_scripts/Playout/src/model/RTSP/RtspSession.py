import random
#import socket
import time

from definitions import Globals
#from definitions.DefObjects import rtspVerbEnum, SessionStateEnum
from definitions.SessExceptions import RTSP_Command_Err
from model.MimeBasedSession import MimeBasedSession
from model.RTSP import SessionStateEnum, rtspVerbEnum
from model.Session import Session

class RtspSession(MimeBasedSession):
    def __init__(self,assets,stb_addr,GlobalCseq,streamer_id,numSess,getAssetBitrate,sendingThread,scheduler):
        Session.__init__(self,assets,stb_addr,streamer_id,numSess,sendingThread,scheduler)
        self.cfg = Globals.cfg
        self.state = SessionStateEnum.INIT
        self.headers = {}
        self.asset = assets
        if(getAssetBitrate):
            self.bitrate = Globals.managerObj.get_asset_bitrate(self.assets.id)
        self.headers["Scale"] = 1

        stb_split =  stb_addr.split(":")
        self.destinationIP  = stb_split[0]
        self.destinationPort = stb_split[1]
        self.GlobalCseq = GlobalCseq
        self.setup_headers = ["Require","CSeq"]
        self.play_headers = ["CSeq","Session","Scale","Range"]
        self.pause_headers = ["CSeq","Session"]
        self.teardown_headers = ["CSeq","Session"]
        self.describe_headers = ["CSeq","Accept"]

        self.setup_content = None
        self.getparams_content = None


        self.session_id = ""
        self.posision = 0
        self.CloseSession = False

        self.Connect()

    def isPlaying(self):
        return (SessionStateEnum.PLAY_RECEIVED<=self.state<SessionStateEnum.TEARDOWN_SENT)


    def handle_DESCRIBE_reply(self,msg):
        raise NotImplementedError

    def handle_SETUP_reply(self,msg):
        if "Session" in msg.headers:
            self.set_session_id(msg.headers["Session"])
            return True
        return False


    def handle_PLAY_reply(self,msg):
        pass
#        if "Scale" in msg.headers:
#            self.setCurrentScale(float(msg.headers["Scale"]))
#            if(float(msg.headers["Scale"])!=1):
#                Session.do_trickplay(self,time.time(),float(msg.headers["Scale"]))

    def handle_PAUSE_reply(self,msg):
        Session.do_trickplay(self,time.time(),0)

    def handle_GETPARAMS_reply(self,msg):
        raise NotImplementedError

    def handle_TEARDOWN_reply(self,msg):
        raise NotImplementedError
        pass


    def exitTrickPlay(self):
        self.session_log.debug("exit TP")
        Session.exitTrickPlay(self)
        self.rtsp_play("now","","1.000")

    def set_session_id(self,session_id):
        self.headers["Session"]  = session_id
        self.session_id = session_id

    def handle_rtsp_request(self,command,headers,content):
        write_buffer = self.build_rtsp_request(self.get_rtsp_url(command),headers,content)
        return self.rtsp_send(write_buffer)

    def allocate(self):
        self.handle_rtsp_request(rtspVerbEnum.SETUP,self.setup_headers,self.setup_content)
        self.state = SessionStateEnum.SETUP_SENT


    def doSETUP(self):
        self.allocate()


    def doPlay(self):
        self.session_start_time = time.time()
        self.rtsp_play("0","","1.000")

    def doDESCRIBE(self):
        pass

    def get_rtsp_url(self,command, selected_asset = None):
        return NotImplemented

    def rtsp_get_parameters(self):
        return NotImplemented

    def rtsp_play(self,s_npt,e_npt,scale = 1):
        if not "Session" in self.headers:
            self.state = SessionStateEnum.CLOSED
            raise RTSP_Command_Err("Error cannot send PLAY request - session has no session id",self,None,1)


        self.headers["Scale"] =   str(scale)
        self.headers["Range"]  =  "npt=%s-%s" % (s_npt, e_npt)
        self.handle_rtsp_request(rtspVerbEnum.PLAY,self.play_headers,None)
        self.state = SessionStateEnum.PLAY_SENT



    def rtsp_describe(self):
        self.handle_rtsp_request(rtspVerbEnum.DESCRIBE,self.describe_headers,None)
        self.state = SessionStateEnum.DESCRIBE_SENT


    def rtsp_pause(self):
        self.handle_rtsp_request(rtspVerbEnum.PAUSE,self.pause_headers,None)
        self.state = SessionStateEnum.PAUSE_SENT

    def end(self):
#        self.end()
        self.CloseSession = True
        self.rtsp_teardown()

    def start (self):
        return NotImplemented

    def rtsp_teardown(self):
        self.handle_rtsp_request(rtspVerbEnum.TEARDOWN,self.teardown_headers,None)
        self.state = SessionStateEnum.TEARDOWN_SENT

    def BuildRequest(self, url, headers, content):

        return super(RtspSession, self).BuildRequest(url, headers, content)


    def build_rtsp_request(self,command,headers,content=None):
        buffer = command + "\r\n"
        for header in headers:
            if(header == "Content-Length" and content!=None):
                buffer+= header + ": " + str(len(content)) + "\r\n"
            elif header == "CSeq":

                cseq = self.GlobalCseq.GetNextCseq(self)
#                    self.session_cseq_dict[cseq] = self
                buffer+= header + ": " + str(cseq) + "\r\n"
            else:
                if header in  self.headers :
                    buffer+= header + ": " + self.headers[header].strip() + "\r\n"
                else:
                    print "Error composing " + command + " command header " + header +" is not in the session dictionary"

        buffer += "\r\n"
        if(content!=None):
            buffer+=content
        return buffer

    def rtsp_send(self,buffer):
        command = buffer.split(" ")[0]
#        print "-> Sending %s command:\n%s\n" % (command,buffer)

        self.session_log.debug( ">>Session Number = " + str(self.session_id) + " command: RTSP_" + command + " \""  + buffer.replace("\r\n"," ") + "\"")
        self.sendingThread.AddMsg(self,buffer)


    def do_trickplay(self,time,tp_command):
        Session.do_trickplay(self,tp_command)

        if(tp_command.start == "NOW"):
            tp_command.start = tp_command.start.lower()
        if(tp_command.end == "END"):
            tp_command.end = tp_command.end.lower()
        if(tp_command.end == "0"):
            tp_command.end = "0.000"
        self.rtsp_trick_play(tp_command.mode,tp_command.scale,tp_command.start.lower(),tp_command.end.lower())
        self.scheduler.addNewTask(self.trick_exit_time,self.exitTrickPlay)

    def rtsp_trick_play(self,mode, scale, s_npt, e_npt):
        if(self.state<2) and (self.state <10):
            return
        if self.cfg.slow_motion == 1:
            slow_scales = [1,2,4,8,16,32,64,3,5,6,7]
            if scale=="1":
                slow=str(random.choice(slow_scales))
            else:
                slow="1"
        else:
            slow="1"

        if self.cfg.slow_motion == 1:
            actual_scale = float(scale/slow)
        else:
            actual_scale = float(scale)

        if (mode == "R" or mode == "P"):
            self.rtsp_play( s_npt,e_npt,actual_scale)
        elif (mode == "U"):
            self.rtsp_pause()

#    def __del__(self):
#        if (Globals.cfg.rtsp_close_socket_once == 1):
#            self.connection_socket.close()