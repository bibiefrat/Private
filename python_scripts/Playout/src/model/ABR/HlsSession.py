import datetime
import re
import time
from ConfigReader import cfg
#from definitions.Logger import timeit
from model.ABR import AbrSessionProfile, Fragment, AbrAssetType, ManifestParsingErr
from model.ABR.AbrSession import AbrSession

class HlsSession(AbrSession):
    def __init__(self, assets, stb_addr, streamer_id, numSess, sendingThread, scheduler):
        super(HlsSession, self).__init__(assets, stb_addr, streamer_id, numSess, sendingThread, scheduler)
        self.profile = AbrSessionProfile.HLS
        self.device_profile = cfg.hls_device_profile
        self.fragmentListReg =  re.compile(r"#EXTINF:(?P<length>.*),\nLevel\((?P<Level>.*)\)/Segment\((?P<Segment>.*)\)")

    def handle_manifest_response(self, msg):
        try:
            if(msg.find("EXT-X-STREAM")>0):
                self.session_log.debug("received manifest data")
                for line in msg.split("\n"):
                    if(not line.startswith("#") and len(line)>0):
                        level = line[line.find("(")+1:line.find(")")]
#                        self.session_log.devel("found level in manifest " + level)
                        self.levels[int(level)] = line
#                self.session_log.devel("total " + str(len(self.levels)) + " levels in manifest")
#            self.session_log.devel(msg)
            super(HlsSession, self).handle_manifest_response(None)
        except :
            raise ManifestParsingErr(self.session_id,"Unable to parse manifest response",self.last_request_sent,msg)


    def handle_fragment_list_response(self,msg):
        try:
#            self.session_log.devel(msg)
            new_fragments = self.fragmentListReg.findall(msg)
            self.session_log.debug("found %d fragments - start parsing list "%len(new_fragments))
            for fragment in new_fragments:
                self.fragments.append(Fragment(fragment[0],fragment[1],fragment[2],"",self.profile))

            if(self.fragments_requested == 0):
                self.selected_fragment = self.fragments.get_fragment()

#            self.session_log.debug("fragments parsed " + str(len(self.fragments)) + " fragments found")

            if(self.fragments_requested == 0 or self.live):
                self.request_next_fragment()
        except :
            raise

#    @timeit
    def handle_fragment_response(self):
        super(HlsSession, self).handle_fragment_response()
#        self.fragments.remove(self.selected_fragment)
        self.selected_fragment = self.fragments.get_fragment()
        if(self.asset_type == AbrAssetType.OPEN_BUFFER and len(self.fragments)==3 and not self.open_buffer_live_switched):
            self.live = True
            self.open_buffer_live_switched = True



    def handle_fragment_start(self):
        fragment_delta = datetime.timedelta(seconds=float(self.selected_fragment.length))
        fragment_delta_length  = fragment_delta.seconds + (fragment_delta.microseconds / 1.0E6)
        if(self.live):
            self.scheduler.addNewTask(time.time() +fragment_delta_length,self.request_fregments_list)
        else:
            self.scheduler.addNewTask(time.time() +fragment_delta_length,self.request_next_fragment)
#        self.state =   AbrSessionStateEnum.FRAGMENT_REQUEST_RECEIVED





