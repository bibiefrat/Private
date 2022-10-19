import libxml2
import logging
import random

import urllib
import time
import urllib2
from definitions import Globals, SessExceptions

from model.LSCP import LscpStateEnum, LSCP_Op_code_enum, LSCP_Request
from model.Session import Session


class LscpSession(Session):
    def __init__(self,assets, stb_addr, streamer_id, numSess,sendingThread,scheduler ):
        Session.__init__(self,assets,stb_addr,streamer_id,numSess,sendingThread,scheduler )
       # self.pid = None        
        self.srvGroup = str(self.cfg.service_group).zfill(12)
        self.loop_mode = self.cfg.loop_mode
        self.eos_flag = False
        self.state = LscpStateEnum.LSCP_INIT
        self.session_log.info("Session init")
        self.next_tp_command = None


    def isPlaying(self):
        return (LscpStateEnum.LSCP_PLAY_RECEIVED<=self.state<LscpStateEnum.LSCP_DONE_RECEIVED) and self.active


    def generate_random_session_id(self):
        time1 = str(int(time.time() * 1000))
        try:
            new = "%d%s" % (random.randint(0, 100000), time1)
        except Exception, e:
            print e
        return urllib.quote_plus(new)

    def handle_translate_response(self,response):
        parse_fx_id = libxml2.parseDoc(response)
        fx_id = Globals.parser.parse_response(parse_fx_id, "//X")
        parse_fx_id.freeDoc()
        self.session_id =fx_id
        self.state =  LscpStateEnum.LSCP_ALLOCATE_END

    def handle_status_response(self):
        Session.do_trickplay(self,time.time(),self.next_tp_command)
        self.lscp_trick_play()
        self.scheduler.addNewTask(self.trick_exit_time,self.exitTrickPlay)



    def handle_allocate_response(self,response):
        if "Fail" in response or "fail" in response:
            self.session_log.error("Allocation Failed Due to: \"%s\"" % str(response))
            raise SessExceptions.SessAllocate_Err(self.private_ID, response, "")

        else:
            res = libxml2.parseDoc(response)
            if (str(res).find("error>")) != -1 :
                error_res = Globals.parser.parse_response(res, "//X/error")

                if error_res !='':
                    self.session_log.error("Allocation Failed Due to: \"%s\"" % str(error_res))
                    raise SessExceptions.SessAllocate_Err(self.private_ID, error_res, "")

            self.stream_handle = Globals.parser.parse_response(res, "//X/info/stream_handle")
            self.streamer = Globals.parser.parse_response(res, "//X/info/streamer_addr")
            sessID = Globals.parser.parse_response(res, "//X/url")
            # Finding the session ID
            self.session_int = Globals.parser.parse_response(res,"/X/id/fx_id")
            res.freeDoc()

            translate_url = "http://%s/translate_session_id?to_string=%d&id=%s" % (str(Globals.managerObj.manager_ip_port), 1, str(self.session_int))

            self.streamerIP = self.streamer.split(":")[0]
            self.server = self.streamerIP
            self.port = 2001


            self.session_log.devel("Opening URL has succeeded ")
            par_response = Globals.parser.url_sess_response(sessID)
            self.session_string = str(par_response[0])

            request = urllib2.Request(translate_url)
            self.sendingThread.AddMsg(self,request)
            self.state = LscpStateEnum.LSCP_TRANSLATE_URL

    def allocate(self):
        self.state = LscpStateEnum.LSCP_ALLOCATE_START
        url = "%s%s/mng_session_allocate?size=%d&internal_asset_id=11111111111" % (Globals.managerObj.getHTTP(), Globals.managerObj.manager_ip_port, 1)
#        for asset in self.assets:
        url += "&seg_start=%s&seg_end=%s&asset_type=2&size=0&size=0&size=0&asset_id=%s" % (self.assets.start, self.assets.end, urllib.quote_plus(self.assets.id))
        self.session_number = self.generate_random_session_id()
        if int(self.streamer_id) == 0 :
            streamer = ""
        else:
            streamer = "&streamer_id=%s" % self.streamer_id
        final_url = "%s&loop=%d&service_group=%s&type=1&fx_id=%s&initiator=QA_lab&stb_id=0%s&abr_type=-1" % (url,self.loop_mode, self.srvGroup, self.session_number,streamer)
        request = urllib2.Request(final_url)
        self.sendingThread.AddMsg(self,request)



        return ""

    def start(self):
        self.session_start_time = time.time()

        if(self.manager.mng_set_stb_ip(self.streamerIP,self.session_number,self.stb_addr) == True):
            self.lscp_play()
        else :
            self.end()


    def exitTrickPlay(self):

        self.session_log.info("exit trick play scale %d",self.next_tp_command.scale)

        Globals.trickplay_mixer.exit_tp_mode(self.next_tp_command.scale)
        self.inTrickPlay = False
        if(self.isPlaying()):
            if(not self.active): print "*****************************************"
            self.lscp_player(LSCP_Op_code_enum.LSCP_PLAY, "1","1", "NOW", "END", "1")

    def lscp_play(self):

        self.state = LscpStateEnum.LSCP_PLAY_SENT

        self.trick_duration = 0
        self.trick_init_time  = 0
        self.trick_exit_time = 0

        if Globals.cfg.start_npt != 0:
            self.lscp_player(LSCP_Op_code_enum.LSCP_PLAY, "1","1", "NOW", "END", "1")
        else:
            self.lscp_player(LSCP_Op_code_enum.LSCP_PLAY, "1","1", "0", "END", "1")
 #       if Globals.cfg.start_npt != 0:
 #           self.lscp_player(LSCP_Op_code_enum.LSCP_PLAY, "1","1", "2200000", "END", "1")
 #       else:
 #           self.lscp_player(LSCP_Op_code_enum.LSCP_PLAY, "1","1", "2200000", "END", "1")





    def Lsc_send(self,request):
       self.sendingThread.AddMsg(self,str(request))


    def lscp_player(self, op_code, scale,slow, s_npt, e_npt, wait):
#        log2 = logging.getLogger("LSCP Player")

        if(op_code == LSCP_Op_code_enum.LSCP_PLAY):
            self.state = LscpStateEnum.LSCP_PLAY_SENT
        elif (op_code == LSCP_Op_code_enum.LSCP_PAUSE):
            self.state = LscpStateEnum.LSCP_PAUSE_SENT
        elif (op_code == LSCP_Op_code_enum.LSCP_RESUME):
            self.state = LscpStateEnum.LSCP_PLAY_SENT
        elif (op_code == LSCP_Op_code_enum.LSCP_STATUS):
            self.state = LscpStateEnum.LSCP_STATUS_SENT


        request = LSCP_Request(self.stream_handle,s_npt,e_npt,op_code,scale,slow)

        try:
            self.session_log.debug( ">>Session Number = " + str(self.session_id) + " op_code: " +LSCP_Op_code_enum.tostring(op_code)
                        + " scale: " + str(scale) + " start: " + str(s_npt) + " end: " +str(e_npt) )

            self.Lsc_send(request)

        except Exception,e:
            Globals.banner_msg("Session Number = " + str(self.session_id) + " operation: "
                               +LSCP_Op_code_enum.tostring(op_code) + " scale: " +str(scale) + " start_npt " + str(s_npt)
                                +" end_npt "+str(e_npt)+ " " +str(e),"error",self.session_log)


    def do_trickplay(self,time,tp_command = None):
        self.inTrickPlay = True
        self.next_tp_command = tp_command
        self.lscp_status()


    def lscp_trick_play(self):

        if(self.next_tp_command is not None):

            if(int(self.current_npt)<1000 and self.next_tp_command.scale<0):
                self.next_tp_command.start = abs(random.randint(int(self.current_npt),int(self.duration*1000)))
                self.current_npt = self.next_tp_command.start
                self.next_tp_command.end = "0"


            self.__lscp_trick_play__(self.next_tp_command.mode,
                self.next_tp_command.scale,self.next_tp_command.start,
                self.next_tp_command.end,self.next_tp_command.wait)


    def __lscp_trick_play__(self, mode, scale, s_npt, e_npt,  wait):

        if Globals.cfg.slow_motion == 1:
            slow_scales = [1,2,4,8,2,6,10,8,9,3,5]
            if scale=="1":
                slow=str(random.choice(slow_scales))
            else:
                slow="1"
        else:
            slow="1"


        log3 = logging.getLogger("TrickPlay")
        if(mode == "U"):
            command = LSCP_Op_code_enum.LSCP_PAUSE
        elif(mode == "R"):
            command = LSCP_Op_code_enum.LSCP_RESUME
        elif(mode == "P"):
            command = LSCP_Op_code_enum.LSCP_PLAY

        if(scale!=0):
            self.state = LscpStateEnum.LSCP_PLAY_SENT
        else:
            self.state = LscpStateEnum.LSCP_PAUSE_SENT


        response = self.lscp_player(command, scale,slow, s_npt, e_npt, wait)


        return  response

    def lscp_status(self):

        self.lscp_player(LSCP_Op_code_enum.LSCP_STATUS, 0,"1", 0, 0, "1")




    def end(self):
        Session.end(self)
        try:

            url = "%s%s/mng_session_teardown?type=1&fx_id=%s" % (Globals.managerObj.getHTTP(), self.manager.manager_ip_port, self.session_number)

            if int(self.loop_mode) == 0 :
                request = urllib2.Request(url)
                self.state = LscpStateEnum.LSCP_EOS_START
                self.sendingThread.AddMsg(self,request)


        except urllib2.URLError, err:
            raise SessExceptions.Manager_Err(err.reason, url)


