import random
import string
from definitions import Globals
from definitions.SessExceptions import SessCreate_Err
from model.RTSP.RtspSession import RtspSession


class NGODSession(RtspSession):
    def __init__(self,assets,stb_addr,GlobalCseq,streamer_id,numSess,sendingThread,scheduler):
        RtspSession.__init__(self,assets,stb_addr,GlobalCseq,streamer_id,numSess,True,sendingThread,scheduler)

        self.on_demand_session_id = ""
        asset_split = str(self.asset.id).split("::")
        # asset format for NGOD session should be: something::something
        if(len(asset_split)<2):
            raise SessCreate_Err("Wrong asset format for NGOD session please check asset.list file "
                                 "(Asset format for NGOD session should be: something::something)")

        self.setup_content = "o=- 06998315000000408000000000451a11 0 IN IP4 10.16.68.61\r\ns=\r\nt=0 0\r\na=X-playlist-item: %s %s 0.000000-\r\nc=IN IP4 0.0.0.0\r\nm=video 0 udp MP2T\r\n"%(asset_split[0],asset_split[1])
        self.headers["Streamcontrolproto"]="rtsp"
        self.headers["Require"]="com.comcast.ngod.r2"
        self.headers["Volume"] = "library"
        self.headers["Content-type"] = "application/sdp"
        self.headers["Content-length"] = str(len(self.setup_content))
        self.headers["Transport"] = "Transport: 2T/DVBC/UDP;unicast;client=000000000000;"\
            "bandwidth=%s;destination=%s;client_port=%s;sop_group=%s"% (str(self.bitrate),str(self.destinationIP),str(self.destinationPort),str(self.cfg.geo_id))
        self.setup_headers.extend(["Streamcontrolproto","Volume","Content-type","Transport","Content-length","Ondemandsessionid"])
        NGOD_extra_headers =   ["Ondemandsessionid","Require","Content-type"]
        self.play_headers.extend(NGOD_extra_headers)
        self.pause_headers.extend(NGOD_extra_headers)
        self.teardown_headers.extend(NGOD_extra_headers)


    def get_rtsp_url(self,command, selected_asset = None):
        url = command +" rtsp://%s:554 RTSP/1.0" % (str.strip(str(Globals.managerObj.manager_ip)))
        return url

    def allocate(self):
        self.on_demand_session_id = ''.join ([random.choice (string.hexdigits[:16]) for x in range (32)])
        self.headers["Ondemandsessionid"]=self.on_demand_session_id
        RtspSession.allocate(self)

    def start (self):
#        self.rtsp_play("0","","1.000")
         self.allocate()

    def reset_url(self):
        pass



