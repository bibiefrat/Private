import urllib
import libxml2
import random
import datetime
import time

from ConfigReader import cfg
from definitions.DefObjects import PlayoutModeEnum
from definitions.Globals import checkByxPath
#from definitions.Logger import timeit
from model.ABR import AbrSessionStateEnum, Fragments, AbrSessionType, SessionDecorators, parse_url, AbrAssetType, ManagerAllocationErr, get_server_as_url
from model.MimeBasedSession import MimeBasedSession




class AbrSession(MimeBasedSession):
    def __init__(self, assets, stb_addr, streamer_id, numSess, sendingThread, scheduler):
        super(AbrSession, self).__init__(assets, stb_addr, None, numSess, sendingThread, scheduler)
        self.profile = ""
        self.levels = {}
        self.audio_levels = {}
        self.device_profile = ""
        self.last_request_sent = ""

        self.open_buffer_live_switched = False
        self.last_fragment_response_time = 0
        self.state = AbrSessionStateEnum.INIT
        self.live =  assets.end == "END" and assets.start == "LIVE"

        self.startTime =assets.start
        self.endTime = assets.end
        self.channel = assets.id

        self.asset_type = assets.asset_type

        self.fragments = Fragments(self.asset_type)

        self.headers["Accept"] = "*/*"
        self.headers["User-Agent"] = "PlayoutScript"
        self.headers["Connection"]= "Keep-Alive"
        self.selected_level = ""
        self.TmpBuffer = None


        #for statistics
        self.fragments_requested = 0
        self.fragment_request_time = 0
        self.avg_fragment_respnse_time = 0
        self.manifest_request_time = 0
        self.level_changed = False
        self.request_url = ""

        self.selected_fragment = None


        self.fragment_content_length = 0
        self.fragment_content_counter = 0

        if(cfg.playout_mode == PlayoutModeEnum.ABR_STATIC):
            self.type = AbrSessionType.STATIC
        elif(cfg.playout_mode == PlayoutModeEnum.ABR_DYNAMIC):
            self.type =  AbrSessionType.DYNAMIC
#        self.type = type
        if(self.type == AbrSessionType.DYNAMIC):
            self.port = 80
            self.Connect()
            self.headers["Host"] = self.server
        else:
            self.server = streamer_id.split(":")[0]
            self.port =  int(streamer_id.split(":")[1])
            self.Connect()
            self.headers["Host"] = streamer_id
        self.session_log.info("new " + type(self).__name__  + " session " + self.channel + " " + assets.start + " - " + assets.end)





    def SendRequest(self,request):
        self.last_request_sent = request
        msg = self.BuildRequest("GET "+ request + " HTTP/1.1" ,["Accept","User-Agent","Host","Connection"],None)
        if(request.startswith("/")):
            request = request.replace("/","",1)

        self.session_log.info( get_server_as_url(self.server,self.port) + request.replace("$","%24") )
        self.sendingThread.AddMsg(self,msg)


    @SessionDecorators.manifest_request_decorator
    def request_manifest(self,request = None):
        # the request argument is set by the decorator
#        self.session_log.info("http://" + self.server+":" +str(self.port) + request)
        self.manifest_request_time = time.time()
        self.SendRequest(request)
        self.state = AbrSessionStateEnum.MANIFEST_REQUEST_SENT

    @SessionDecorators.fragment_list_request_decorator
    def request_fregments_list(self,request=None):
        #request argument is set by the decorator
        self.SendRequest(request)
        self.state = AbrSessionStateEnum.FRAGMENT_LIST_REQUEST_SENT


    @SessionDecorators.fragment_request_decorator
    def request_next_fragment(self,request):
        if(self.selected_fragment is  None):
            self.state = AbrSessionStateEnum.CLOSED
            return

        if(self.level_changed):
            self.session_log.devel("changing level")
            if(not self.live):
                self.request_fregments_list()
            self.level_changed = False
        else:
            if(self.type == AbrSessionType.STATIC):
                self.session_log.info("playing segment " +str(self.selected_fragment) +" for " + self.selected_fragment.length + " seconds " + "{"
                                      + str(datetime.datetime.utcfromtimestamp(float(self.selected_fragment.timestamp)/10000000.0)) + "}")
            else:
                self.session_log.info("playing segment " +str(self.selected_fragment) +" for " + self.selected_fragment.length + " seconds ")

            self.SendRequest(request)

            self.fragment_request_time = time.time()

            self.fragments_requested+=1
            self.state = AbrSessionStateEnum.FRAGMENT_REQUEST_SENT


    def start (self):
        if(self.type ==AbrSessionType.STATIC):
            self.request_manifest()
        else:
            self.Allocate()




    def handle_manifest_response(self,msg):
        if(cfg.start_at_random_level =="0"):
            self.selected_level = self.GetRandomLevel()
        else:
            if(len(self.levels)>=int(cfg.start_at_random_level)):
                self.selected_level = sorted(self.levels.keys())[int(cfg.start_at_random_level-1)]
            else:
                self.selected_level = sorted(self.levels.keys())[len(self.levels)-1]








    def GetRandomLevel(self):
        return random.choice(self.levels.keys())



    def change_level(self):
        self.selected_level = self.GetRandomLevel()
        self.level_changed = True
        self.scheduler.addNewTask(time.time() +datetime.timedelta(seconds=random.randint(30,31)).seconds,self.change_level)
        self.session_log.info("level change at next fragment request")




    def handle_fragment_response(self):
        response_time = 0

        if(self.fragment_request_time !=0):
            response_time = time.time() - self.fragment_request_time
            if(response_time > datetime.timedelta(seconds=1).seconds):
                self.session_log.warning("fragment response time is " + str(response_time)  +" "+ str(self.connection_socket.getsockname()))
            self.last_fragment_response_time = response_time
            if(self.avg_fragment_respnse_time!=0):
                self.avg_fragment_respnse_time = (self.avg_fragment_respnse_time + response_time) /2
            else:
                self.avg_fragment_respnse_time = response_time
            self.session_log.info("avg response time:" + str(self.avg_fragment_respnse_time))


#        self.session_log.debug("next fragment " + str(self.selected_fragment))






    def Allocate(self):
        if(self.asset_type == AbrAssetType.VOD_ASSET):
	    if(cfg.use_rsdvr_abr_vod==1):
		self.SendRequest("/abr_dvr"+self.channel+"/"+self.device_profile)
	    else:
            	self.SendRequest("/abr_vod"+self.channel+"/"+self.device_profile)
        else:
            self.SendRequest("/rolling_buffer/"+self.channel.strip("LIVE$")+"/"+self.startTime+"/"+self.endTime+"/" +self.device_profile)
        self.state = AbrSessionStateEnum.MANAGER_MANIFEST_REQUEST_SENT

    def handle_manager_response(self, msg):
        try:
            if(self.asset_type == AbrAssetType.VOD_ASSET):
                url = checkByxPath(libxml2.parseDoc(msg),"/allocation_result/url")
            else:
                url = checkByxPath(libxml2.parseDoc(msg),"/rolling_buffer_allocation_result/url")

            serverPort,uri = parse_url(url)
            self.streamer_url = uri
            self.SetServerPort(serverPort)
    #        self.SetServerPort("192.168.5.65:5555")
            self.headers["Host"] = serverPort
        except :
            raise ManagerAllocationErr(self.session_log.name,msg,self.last_request_sent)




    def isPlaying(self):
        return self.state >=AbrSessionStateEnum.FRAGMENT_LIST_REQUEST_RECEIVED

    def do_trickplay(self, time, tp_command):
        super(AbrSession, self).do_trickplay(time, tp_command)
#        self.fragment_index +=tp_command.scale
#        self.fragments_iter+=tp_command.scale
        self.scheduler.addNewTask(self.trick_exit_time,self.exitTrickPlay)


    def handle_fragment_start(self):
        pass






