import datetime
import random
import time
from ConfigReader import cfg
from definitions.Globals import checkByxPath
from definitions.SessExceptions import MisconfigurationError
from model.ABR import AbrSessionProfile, get_xml_dox_from_msg, list_checkByxPath, Fragment, Fragments, AbrSessionStateEnum, AbrAssetType, ManifestParsingErr
from model.ABR.AbrSession import AbrSession

class SmoothSession(AbrSession):
    def __init__(self, assets, stb_addr, streamer_id, numSess, sendingThread, scheduler):
        super(SmoothSession, self).__init__(assets, stb_addr, streamer_id, numSess, sendingThread, scheduler)
        self.profile = AbrSessionProfile.SMOOTH
        if(assets.asset_type == AbrAssetType.LIVE or assets.asset_type == AbrAssetType.OPEN_BUFFER):
            raise MisconfigurationError("cannot config live or open buffer with smooth session")
        self.device_profile = cfg.smooth_device_profile
        self.audio_fragments = Fragments(assets.asset_type)
        self.streamer_url = None
        self.sent_video_request = False



    def handle_manifest_response(self, msg):
        try:
            if(self.streamer_url):
                self.streamer_url = self.streamer_url.rstrip("Manifest")
            dom = get_xml_dox_from_msg(msg)

            video_url = checkByxPath(dom,"/SmoothStreamingMedia/StreamIndex[@Type='video']/@Url")
            video_levels = list_checkByxPath(dom,"/SmoothStreamingMedia/StreamIndex[@Type='video']/QualityLevel/@Bitrate")
            for level in video_levels:
                self.levels[level] = video_url.replace("{bitrate}",level).split("/")[0]

            video_fragment_url = video_url.split("/")[1]
            video_fragment_list =list_checkByxPath(dom,"/SmoothStreamingMedia/StreamIndex[@Type='video']/c/@d")
            start_time =  checkByxPath(dom,"/SmoothStreamingMedia/StreamIndex[@Type='video']/c/@t")
            if(start_time):
                time_count = int(start_time)
            else:
                time_count = 0
            for fragment in video_fragment_list:
                fragment_length =  str(int(fragment)/10000000.0)
                self.fragments.append(Fragment(fragment_length,"0",str(time_count),video_fragment_url.replace("{start time}","%s"),self.profile))
                time_count+=int(fragment)

            audio_url = checkByxPath(dom,"/SmoothStreamingMedia/StreamIndex[@Type='audio']/@Url")
            audio_levels = list_checkByxPath(dom,"/SmoothStreamingMedia/StreamIndex[@Type='audio']/QualityLevel/@Bitrate")
            for level in list(audio_levels):
                self.audio_levels[level] = audio_url.replace("{bitrate}",level).split("/")[0]

            audio_fragment_url = audio_url.split("/")[1]
            audio_fragment_list =list_checkByxPath(dom,"/SmoothStreamingMedia/StreamIndex[@Type='audio']/c/@d")
            start_time =  checkByxPath(dom,"/SmoothStreamingMedia/StreamIndex[@Type='audio']/c/@t")
            if(start_time):
                time_count = int(start_time)
            else:
                time_count = 0

            for fragment in audio_fragment_list:
                fragment_length =  str(int(fragment)/10000000.0)
                self.audio_fragments.append(Fragment(fragment_length,"0",str(time_count),audio_fragment_url.replace("{start time}","%s"),self.profile))
                time_count+=int(fragment)

            super(SmoothSession, self).handle_manifest_response(None)
        except :
            raise  ManifestParsingErr(self.session_id,"Unable to parse manifest response " +msg,self.last_request_sent)

    def request_fregments_list(self, request=None):
        self.selected_fragment = self.fragments.get_fragment()
        self.request_next_fragment()
        self.sent_video_request = True


    def handle_fragment_response(self):
        super(SmoothSession, self).handle_fragment_response()
        if(self.state == AbrSessionStateEnum.FRAGMENT_REQUEST_RECEIVED):

            self.selected_fragment = self.audio_fragments.get_fragment()
            self.request_next_fragment()
            self.sent_video_request = False
            self.state = AbrSessionStateEnum.AUDIO_FRAGMENT_REQUEST_SENT

        elif (self.state == AbrSessionStateEnum.AUDIO_FRAGMENT_REQUEST_RECEIVED):
#            self.session_log.warn("got audio fragment")
            self.selected_fragment = self.fragments.get_fragment()
            self.sent_video_request = True
            self.state = AbrSessionStateEnum.FRAGMENT_REQUEST_SENT


    def handle_fragment_start(self):
        super(SmoothSession, self).handle_fragment_start()
        if(self.state == AbrSessionStateEnum.AUDIO_FRAGMENT_REQUEST_RECEIVED):
            fragment_delta = datetime.timedelta(seconds=float(self.selected_fragment.length))
            fragment_delta_length  = fragment_delta.seconds + (fragment_delta.microseconds / 1.0E6)
            self.scheduler.addNewTask(time.time() +fragment_delta_length,self.request_next_fragment)

    def change_level(self):
        self.selected_level = self.GetRandomLevel()

        self.scheduler.addNewTask(time.time() +datetime.timedelta(seconds=random.randint(30,60)).seconds,self.change_level)
        self.session_log.info("level change at next fragment request")


