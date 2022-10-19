import urlparse


from model.RTSP import SessionStateEnum
from model.RTSP.RtspSession import RtspSession

class RtspRollingBuffer(RtspSession):
    def __init__(self,assets,stb_addr,GlobalCseq,streamer_id,numSess,sendingThread,scheduler):
        RtspSession.__init__(self,assets,stb_addr,GlobalCseq,streamer_id,numSess,False,sendingThread,scheduler)

        self.channel = assets.id

        self.startTime = assets.start
        self.endTime = assets.end


        self.setup_headers.remove("Require")
        self.headers["User-Agent"] = "Playout"
        self.headers["Transport"] = "RTP/AVP/TCP;unicast;interleaved=0-1"
        self.headers["x-mayNotify"] = ""
        self.headers["Accept"] = "application/sdp"
        self.headers["Scale"] = "1.000"
        self.headers["Range"] = "npt="+self.startTime+"-"+ self.endTime
        self.headers["x-reason"] =  "released"
        self.play_headers.extend(["User-Agent"])
        self.setup_headers.extend(["x-mayNotify","User-Agent","Transport" ])
        self.teardown_headers.extend(["x-reason","User-Agent"])
        self.describe_headers.extend(["User-Agent"])
        self.pause_headers.extend(["User-Agent"])

        self.rtsp_url = "rtsp://%s:554/rolling_buffer/%s/%s/%s RTSP/1.0" % (self.server,self.channel,self.startTime,self.endTime)
        self.newUrl = ""



    def reset_url(self):
        self.rtsp_url = "rtsp://%s:554/rolling_buffer/%s/%s/%s RTSP/1.0" % (self.server,self.channel,self.startTime,self.endTime)
    def get_rtsp_url(self, command, selected_asset=None):

        url = command +" " +self.rtsp_url
        return url

    def set_new_url(self,url):
        self.rtsp_url = url +" RTSP/1.0"

    def handleRedirect(self,new_addr):
        parsed =  urlparse.urlparse(new_addr.strip())
        self.server,self.port = parsed.netloc.split(":")
        self.port = int(self.port)
#        self.server = self.server.replace(".7.",".6.")
        sessionid = parsed.path.replace("/","")

        if(self.state == SessionStateEnum.TEARDOWN_RECEIVED):
            sessionid = self.session_id.strip()

        self.rtsp_url = "rtsp://%s:%d/rolling_buffer/%s/%s/%s/%s RTSP/1.0" % (self.server,self.port,self.channel,self.startTime,self.endTime,sessionid)

        if(self.state == SessionStateEnum.SETUP_RECEIVED):
            self.state =SessionStateEnum.DESCRIBE_RECEIVED

        elif (self.state == SessionStateEnum.TEARDOWN_RECEIVED):
            self.state = SessionStateEnum.TEARDOWN_SENT
            self.rtsp_teardown()


    def handle_DESCRIBE_reply(self,msg):
        if( "a" in msg.headers and "control" in msg.headers["a"]):
            self.set_new_url(msg.headers["a"].replace("control:",""))
            return True
        return False




    def set_rtsp_url(self,host):
        pass


#    def allocate(self):
#        self.rtsp_describe()

    def start (self):
        self.rtsp_describe()
        #self.rtsp_describe()
        #self.rtsp_play("0","","1.000",Socket)





