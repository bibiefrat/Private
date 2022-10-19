# File Name: Session.py
import logging


from definitions import Globals

from model.Connection import Connection


class Session(Connection):
    def __setattr__(self, key, value):
        super.__setattr__(self,key,value)
        if(key == "session_id"):
            self.session_log.name = type(self).__name__ + " " + str(self.private_ID) + " " + self.session_id


    def __repr__(self):
        return type(self).__name__ + " " +str(self.private_ID)

    def __init__(self, assets, stb_addr, streamer_id, numSess,sendingThread,scheduler ,port=554):
        Connection.__init__(self,str(Globals.cfg.manager_ip).strip(),port)
        # Class Properties:
        self.private_ID = numSess
        self.session_log = logging.getLogger(type(self).__name__ + " " + str(self.private_ID))
        print str(type(self).__name__ + " " + str(self.private_ID))
        self.active = True
        self.scheduler = scheduler
        self.cfg = Globals.cfg
        self.assets = assets
        self.manager = Globals.managerObj
        self.manager_ip =self.cfg.manager_ip

        self.stb_addr = stb_addr
        self.streamer_id = streamer_id


        self.streamer = ""
        self.session_string = ""
        self.rtsp_session = ""
        self.session_number = None
        self.session_id = ""
        self.duration = assets.duration # sum of all duration assets in play list

        self.trick_duration = 0
        self.trick_init_time  = 0
        self.trick_exit_time = 0



        self.currentScale = 1

        self.sendingThread = sendingThread

        self.session_start_time = 0
        self.current_npt = 0
        self.inTrickPlay = False

    def isPlaying(self):
        raise NotImplementedError

    def end(self):
        self.session_log.info("end of stream")
        self.active = False
        if(self.inTrickPlay):
            self.exitTrickPlay()

        self.cleanUp()



    def cleanUp(self):
        self.session_start_time = 0
        self.trick_duration = 0
        self.trick_init_time  = 0
        self.trick_exit_time = 0






    def shouldExitTrickMode(self,time):
        return time>self.trick_exit_time and self.inTrickPlay



    def shouldTearDown(self,time):
        if(self.session_start_time == 0):
            raise Exception("Session start time not initialized !!!")
        return time>self.session_start_time + self.duration

    def setTotalDuration(self, playList):
        totalDuration = 0
        for asset in playList:
            totalDuration += asset.duration
        return totalDuration

    def do_trickplay(self,time,tp_command):

        self.inTrickPlay = True
        self.currentScale = tp_command.scale
        self.trick_init_time = time
        if(tp_command.scale!=0):
            self.trick_duration = Globals.cfg.command_duration/self.currentScale
        else:
            #TODO: add pause duration to config file
            self.trick_duration = 55
        self.session_log.info("doing trick play at scale %d for %d seconds",tp_command.scale,abs(self.trick_duration))
#        print "tp_duration ="+str(abs(self.trick_duration)) + " at scale: " +str(tp_command.scale)
        self.trick_exit_time = time +abs(self.trick_duration)



    def exitTrickPlay(self):
        self.session_log.info("exit trick play scale %d",self.currentScale)


        Globals.trickplay_mixer.exit_tp_mode(self.currentScale)
        self.inTrickPlay = False
#

    def setCurrentScale(self,scale):
        self.currentScale = scale




    def __str__(self):
        return "main session number = " + str(self.session_number) + "\nmain session string = " + str(self.session_string) + "\nRTSP session = " + str(self.rtsp_session) + "\nStreamer = " + self.streamer + "\n-------------------------------------------------------------------------------------------------------"


