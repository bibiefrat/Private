import logging
import random
import threading

class TrickPlayMixer(object):
    def __init__(self,cfg,parser):
        self.tricker_log = logging.getLogger(type(self).__name__ )
        path = "../"
        self.cfg = cfg
        self.tp_commnads = parser.lscp_tricks(cfg.trickplay_list_path, path)[0]
        self.trick_play_percent = cfg.trick_play_percent
        self.ff_commands = []
        self.rew_commands = []
        self.pause_commands = []
        for command in self.tp_commnads:
            if command.mode == "U":
                self.pause_commands.append(command)
            elif int(command.scale) <0:
                self.rew_commands.append(command)
            else:
                self.ff_commands.append(command)

        self.ff_percent = cfg.ff_percent
        self.rew_percent = cfg.rew_percent
        self.pause_percent = cfg.pause_percent

        self.current_in_ff = 0
        self.current_in_rew = 0
        self.current_in_pause = 0

        self.current_in_ff_lock = threading.Lock()
        self.current_in_rew_lock = threading.Lock()
        self.current_in_pause_lock = threading.Lock()

        self.total_sessions_for_tp = float(cfg.trick_play_percent) / 100*cfg.total_sessions

        self.total_ff_quota = round(float(self.ff_percent)/100*self.total_sessions_for_tp)
        self.total_rew_quota =  round(float(self.rew_percent)/100*self.total_sessions_for_tp)
        self.total_pause_quota = round(float(self.pause_percent)/100*self.total_sessions_for_tp)

        self.command_list = [self.__get_ff_command__,self.__get_rew_command__,self.__get_pause_command__]

        print "total:" + str(self.total_sessions_for_tp) + " ff:" +  str(self.total_ff_quota) + " rew:" + str(self.total_rew_quota) + " pause:" + str(self.total_pause_quota)

    def __get_ff_command__(self):
            try:
                self.current_in_ff_lock.acquire()
                if(self.current_in_ff < self.total_ff_quota):
                    self.current_in_ff+=1
                    return random.choice(self.ff_commands)

            finally:
                self.current_in_ff_lock.release()

    def __get_rew_command__(self):
        try:
            self.current_in_rew_lock.acquire()
            if(self.current_in_rew <  self.total_rew_quota):
                self.current_in_rew+=1
                return random.choice(self.rew_commands)


        finally:
            self.current_in_rew_lock.release()

    def __get_pause_command__(self):
        try:
            self.current_in_pause_lock.acquire()
            if(self.current_in_pause <  self.total_pause_quota ):
                self.current_in_pause+=1
                return random.choice(self.pause_commands)

        finally:
            self.current_in_pause_lock.release()

    def get_command(self):
    #        print "in ff " + str(self.current_in_ff) + " in rew " +  str(self.current_in_rew) + " in pause " + str(self.current_in_pause)
        self.tricker_log.devel("[get_command] in ff " + str(self.current_in_ff) + " in rew " +  str(self.current_in_rew) + " in pause " + str(self.current_in_pause))
        try:
            random.shuffle(self.command_list)
            for command in self.command_list:
                tmp_command = command.__call__()
                if(tmp_command!=None):
                    return tmp_command
            return None

        finally:
            self.tricker_log.devel("after [get_command] in ff " + str(self.current_in_ff) + " in rew " +  str(self.current_in_rew) + " in pause " + str(self.current_in_pause))



    def exit_tp_mode(self,scale):
        self.tricker_log.devel("exit_tp_mode " + str(scale))

        if(scale>0):
            self.current_in_ff_lock.acquire()
            if(self.current_in_ff>0):
                self.current_in_ff-=1
            self.current_in_ff_lock.release()
        elif scale<0:
            self.current_in_rew_lock.acquire()
            if(self.current_in_rew>0):
                self.current_in_rew-=1
            self.current_in_rew_lock.release()
        else:
            self.current_in_pause_lock.acquire()
            if(self.current_in_pause>0):
                self.current_in_pause-=1
            self.current_in_pause_lock.release()

        self.tricker_log.devel("self.current_in_ff=" + str(self.current_in_ff) + " self.current_in_rew=" + str(self.current_in_rew) + " self.current_in_pause=" +str(self.current_in_pause))


