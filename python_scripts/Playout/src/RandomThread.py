# File Name: RandomThread.py

from itertools import izip
#from definitions.DefObjects import LscpStateEnum
from definitions.SessExceptions import Manager_Err#, RTSP_Command_Err
import threading
import time


import logging
import sys
#from definitions import DefObjects
import random
#import string
from bisect import bisect
#import socket
import traceback

#from SessionAllocationThread import Session_Allocation_Thread
#path = os.getcwd()
#from definitions.DefObjects import SessionStateEnum, LscpStateEnum, LSCP_Op_code_enum, NTP_enum,  RTSPStatusCodeEnum, rtspVerbEnum, RTPDatagram
#from definitions.DefObjects import PlayoutModeEnum
from definitions import Globals
#from model.Response import Message
from model.LSCP import LscpStateEnum

path = "../"


def wchoice(objects, frequences, filter=True, normalize=True):
    """wchoice(objects, frequences, filter=True, normalize=True): return
    a function that return the given objects with the specified frequency
    distribution. If no objects with frequency>0 are given, return a
    constant function that return None.

    Input:
      objects: sequence of elements to choose.
      frequences: sequence of their frequences.
      filter=False disables the filtering, speeding up the object creation,
        but less bad cases are controlled. Frequences must be float > 0.
      normalize=False disables the probablitity normalization. The choice
        becomes faster, but sum(frequences) must be 1
    """
    if filter:
        # Test and clean the frequencies.
        if isinstance(frequences, (set, dict)):
            raise "in wchoice: frequences: only ordered sequences."
        if isinstance(objects, (set, dict)):
            raise "in wchoice: objects: only ordered sequences."
        if len(frequences) != len(objects):
            raise "in wchoice: objects and frequences must have the same lenght."
        frequences = map(float, frequences)
        filteredFreq = []
        filteredObj = []
        for freq, obj in izip(frequences, objects):
            if freq < 0:
                raise "in wchoice: only positive frequences."
            elif freq > 1e-8:
                filteredFreq.append(freq)
                filteredObj.append(obj)

        if len(filteredFreq) == 0:
            return lambda: None
        if len(filteredFreq) == 1:
            return lambda: filteredObj[0]
        frequences = filteredFreq
        objects = filteredObj
    else:
        if len(objects) == 1:
            return lambda: objects[0]
            # Here objects is unaltered, so it must have a fast __getitem__

    addedFreq = []
    lastSum = 0
    for freq in frequences:
        lastSum += freq
        addedFreq.append(lastSum)

    # If the choice method is called many times, then the frequences
    # can be normalized to sum 1, so instead of random()*self.sumFreq
    # a random() suffices.
    if normalize:
        return lambda rnd=random.random, bis=bisect: objects[bis(addedFreq, rnd() * lastSum)]
    else:
        return lambda rnd=random.random, bis=bisect: objects[bis(addedFreq, rnd())]


class TrickPlayCommand:
    def __init__(self, is_my_turn, lock):
        self.lock = lock
        self.is_my_turn = is_my_turn

    def setLscp(self, mode, scale, s_npt, e_npt, time_elapsed, wait):
        # Class Properties:
        self.mode = mode
        self.scale = scale
        self.s_npt = s_npt
        self.e_npt = e_npt
        self.time_elapsed = time_elapsed
        self.wait = wait


class RandomTest(threading.Thread):
    def __init__(self, session, trickParams, trickPlayArray,index):
        threading.Thread.__init__(self)
        self.session = session
        self.tricks = trickParams[0]
        self.tricksLength = trickParams[1]
        self.totalDuration = int(Globals.cfg.total_duration)
        self.loop_mode = Globals.cfg.loop_mode
        self.index = index
        self.inter_tp_sleep = Globals.cfg.sleep_after_play
        self.sleep_after_play = Globals.cfg.sleep_after_play
        self.trickPlayArray = trickPlayArray
        self.print_alloc_time = Globals.cfg.print_alloc_time
        self.lsc_tool_play_resume = Globals.cfg.lsc_tool_play_resume
        self.video_change_bitrate = Globals.cfg.video_change_bitrate
        self.audio_change_bitrate = Globals.cfg.audio_change_bitrate
        self.manager = Globals.managerObj
        self.trickPlayArray[self.index].lock.acquire()
        self.trickPlayArray[self.index].scale = 1
        self.trickPlayArray[self.index].lock.release()
        self.trick_play_percent = Globals.cfg.trick_play_percent



    def do_trickplay(self,tp_command):
        try:
            response = self.session.lscp_status()

            current_ntp = response.current_NPT
            if(self.session.session_state == LscpStateEnum.LSCP_EOS or current_ntp == 0 or current_ntp == self.session_end_ntp):
                #Globals.trickplay_mixer.exit_tp_mode(tp_command.scale)
                return response

            if(tp_command.mode == "U"):
                tp_command.scale =0

            #current_position_and_end_ntp = Globals.managerObj.get_current_session_npt(str_session_id)
            if(int(current_ntp)<1000 and tp_command.scale<0):
                tp_command.start = abs(random.randint(int(current_ntp),int(self.session_end_ntp)))
                current_ntp = tp_command.start
                tp_command.end = "0"

            trick_duration = Globals.calculate_sleep_time(tp_command.scale,
                                                          self.session_end_ntp, int(current_ntp))

            self.session.lscp_trick_play(tp_command.mode,
                tp_command.scale,tp_command.start,
                tp_command.end, tp_command.runTime,
                tp_command.wait)

            self.log1.info("----- Session #%d in trick play ---------" % (self.session.private_ID))
            time.sleep(abs(trick_duration))
            response = self.session.lscp_status()
            #Globals.trickplay_mixer.exit_tp_mode(tp_command.scale)

            return response
        finally:
            Globals.trickplay_mixer.exit_tp_mode(tp_command.scale)

    def get_current_npt(self):
        return self.session.lscp_status().current_NPT
    
    def run(self):
        self.log1 = logging.getLogger(RandomTest.getName(self))
        self.log1.info("------------- Entering %s -------------" % (RandomTest.getName(self)))

        try:
            if (self.totalDuration != 0) and (self.totalDuration >= self.session.duration):
                if self.session.duration != 0:
                    runLength = int(self.totalDuration / self.session.duration)
                else:
                    runLength = 1

            else:
                runLength = 1

                # how much time to run each loop!!
                # minimum Real run duration is the session duration as defined in the asset file (-1 for the whole asset)
            real_run_duration = self.session.duration
            orig_run_duration = real_run_duration
            for loop in range(runLength):
                try:
                    begin_time = time.time()

                    self.log1.info("----- Start Session #%d with loop #%d ---------" % (self.session.private_ID, loop))
                    alloc_time = self.session.allocate()

                    if self.print_alloc_time == 1:
                        Globals.global_lock.acquire()
                        Globals.alloc_list.append(alloc_time)
                        Globals.global_lock.release()

                    str_session_id =  str(Globals.managerObj.translate_session_id(self.session.session_id, 0))
                    self.log1.name+= " Session: " +self.session.session_id
                    self.session_end_ntp = Globals.managerObj.get_current_session_npt(str_session_id)[1]

                    self.session.start()

                    self.log1.info("Session Num %s for thread %s " % (self.index, self.session.session_id))
                    #print "thread %s run duration %s " % (self.index , real_run_duration)

                    current_npt =  self.get_current_npt()
                    while (current_npt<= self.session_end_ntp):

                        tp_command = Globals.trickplay_mixer.get_command()

                        if(tp_command!=None):

                            self.do_trickplay(tp_command)

                            current_npt = self.session.current_npt

                            if((current_npt == 0 or self.session.session_state == LscpStateEnum.LSCP_EOS) and (tp_command.scale<0 )):
                                #got eos at beginning of stream from rewind
                                self.session.lscp_play()
                            elif(current_npt == self.session_end_ntp or self.session.session_state == LscpStateEnum.LSCP_EOS):
                                if self.loop_mode != 1:
                                    break

                        else:
                                time.sleep(1)
                                if self.loop_mode != 1:
                                    current_npt+=1000


                        time.sleep(self.sleep_after_play)
                        delta_time = time.time() - begin_time
                        real_run_duration = orig_run_duration - delta_time

                    Globals.global_lock.acquire()                   
                    self.log1.info("++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    self.log1.info("Session #%d Loop #%d has completed successfully " % (self.session.private_ID, loop))
                    #log.info("Session #" + str(self.session.private_ID) + " Loop #" + str(loop) + " has completed succefully ")
                    self.log1.info("++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    Globals.success_counter += 1
                    Globals.global_lock.release()

                    self.log1.info("<<<<<<<<<<<<<<<TEARing DOWN session of thread  # %s in loop %s >>>>>>>>>>>>>>>" % (
                    self.index, loop))

                    self.session.end()

                    real_run_duration = orig_run_duration


                except Manager_Err, err:
                    Globals.global_lock.acquire()
                    self.log1.critical(err)
                    self.log1.critical("The session has ended, and will exit thread!")
                    Globals.failed_counter += 1
                    Globals.global_lock.release()
                    #                        return
                    pass



        except Exception, err:
        #                if hasattr(err, err.reason):
        #                    log.error(exception.reason)
            traceback.print_exc(file=sys.stdout)
            Globals.global_lock.acquire()
            Globals.failed_counter += 1
            self.log1.critical(
                "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< session " + self.session.session_id + " has ended with error!!!!!!!!! >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            self.log1.error(err)
            Globals.global_lock.release()
            return


    def end(self):
        self.session.end()




#class Dispatcher(threading.Thread):
#    def __init__(self, my_threads, command_duration, trick_play_percent, total_duration, max_ses_duration, loop_mode,
#                 trickPlayArray, dispatcher_serial, Sessions_List, lsc_tool_play_resume):
#        threading.Thread.__init__(self)
#        self.threads = my_threads
#        self.trick_play_percent = trick_play_percent
#        self.command_duration = command_duration
#        self.total_duration = total_duration
#        self.max_ses_duration = max_ses_duration
#        self.loop_mode = loop_mode
#        self.trickPlayArray = trickPlayArray
#        self. dispatcher_serial = dispatcher_serial
#        self.Sessions_List = Sessions_List
#        self.lsc_tool_play_resume = lsc_tool_play_resume
#
#    def run(self):
#        log2 = logging.getLogger("Dispatcher")
#        # number of trick commands to run
#        num_of_trick_commands = int((self.trick_play_percent / 100.0) * len(self.threads))
#        log2.info(
#            "**************************** Dispatcher # %s is running - Number of sessions in trick mode : %s \n" % (
#            self.dispatcher_serial, num_of_trick_commands))
#
#        trick_commands_array = []
#        for i in range(num_of_trick_commands):
#            trick_commands_array.append(i)
#        tp_flip_flop = []
#        for i in range(num_of_trick_commands):
#            tp_flip_flop.append(0)
#
#        ## Read the Trick file
#        try:
#            tricks_file = open(path + "/" + "conf/trickplay.lscp", "r")
#        except IOError:
#            log2.critical("Trick file can not be found.\nScript finished")
#            sys.exit()
#
#        all_lines = tricks_file.readlines()
#        play_tricks = []
#
#        for single_lines in all_lines:
#            line = str(single_lines).split(" ")
#            if line[0] == '#':
#                continue
#
#            trick = DefObjects.lscpTricks(line[0], line[1], line[2], line[3], line[4], line[5].rstrip())
#            #play_tricks - this is list containing all trick play commands
#            play_tricks.append(trick)
#
#
#        # the real run duration is 1.5 longer than total duration + longest command duration
#        real_run_duration = 0.0
#        real_run_duration = float((float(self.total_duration) + float(self.command_duration)) * 1.3)
#        log2.debug("************** .Real RUN DURAtion ----> %s \n" % (real_run_duration))
#
#        # time of beginning the trick plays
#        begin_time = time.time()
#        orig_run_duration = real_run_duration
#        # command duration for live rec - either the test duration or the command duration from the ini file - the shorter one
#        real_command_duration = 0
#
#        if (self.loop_mode == 0):
#            while ((real_run_duration) > 0):
#                for i in range(num_of_trick_commands):
#                    #print "DISPATCHER  INDEX IS: ********************" , i
#                    if(self.trickPlayArray[trick_commands_array[i]].lock.acquire(0)):
#                        ff_flag = 1
#                        if tp_flip_flop[i] == 0:
#                            ff_flag = 0
#                            # print "after lock Status %s  for thread %s" % (str(trickPlayArray[trick_commands_array[i]].lock.locked()) , trick_commands_array[i])
#                            old_thread = trick_commands_array[i]
#                            rand_trick_command = random.randint(0, len(play_tricks) - 1)
#                            rand_thread = random.randint(0, len(self.threads) - 1)
#                            # look for thread not in Trick play till you find one
#                            while(1):
#                                if self.trickPlayArray[rand_thread].lock.acquire(0):
#                                    if(self.trickPlayArray[rand_thread].is_my_turn != 1):
#                                        break
#                                    else:
#                                        self.trickPlayArray[rand_thread].lock.release()
#                                        rand_trick_command = random.randint(0, len(play_tricks) - 1)
#                                        rand_thread = random.randint(0, len(self.threads) - 1)
#                                else:
#                                    rand_trick_command = random.randint(0, len(play_tricks) - 1)
#                                    rand_thread = random.randint(0, len(self.threads) - 1)
#                            self.trickPlayArray[rand_thread].is_my_turn = 1
#                            trick_commands_array[i] = rand_thread
#                            #print "setting TP parameter for thread : %s" % (rand_thread)
#                            # calculate trick play duration with considering the scale
#                            if self.command_duration < real_run_duration:
#                                real_command_duration = self.command_duration
#                                if  real_command_duration > self.Sessions_List[rand_thread].duration:
#                                    real_command_duration = self.Sessions_List[rand_thread].duration
#                            else:
#                                real_command_duration = real_run_duration
#                                if  real_command_duration > self.Sessions_List[rand_thread].duration:
#                                    real_command_duration = self.Sessions_List[rand_thread].duration
#                            real_command_duration *= 0.97
#
#                            #actual_TP_duration = int(int(self.command_duration) / abs(int(play_tricks[rand_trick_command].scale)))
#                            actual_TP_duration = int(
#                                int(real_command_duration) / abs(int(play_tricks[rand_trick_command].scale)))
#                            if actual_TP_duration == 0:
#                                actual_TP_duration = 2
#                                #pause is torn after 60 sec so we set it to 55 sec
#                            if (play_tricks[rand_trick_command].mode == "U" and actual_TP_duration >= 60):
#                                actual_TP_duration = 55
#                                #print "<<<<<<<<<<<<<<<< DISPATCHER set TP duration %s for scale %s " % (actual_TP_duration ,play_tricks[rand_trick_command].scale )
#                            #print "setting TP parameter for thread : %s" % (rand_thread)
#                            self.trickPlayArray[rand_thread].setLscp(play_tricks[rand_trick_command].mode,
#                                play_tricks[rand_trick_command].scale, play_tricks[rand_trick_command].start,
#                                play_tricks[rand_trick_command].end, actual_TP_duration,
#                                play_tricks[rand_trick_command].wait)
#                            #                                print "LCSP mode " ,play_tricks[rand_trick_command].mode
#                            #                                print "LCSP scale  ",play_tricks[rand_trick_command].scale
#                            #                                print "LCSP start ",play_tricks[rand_trick_command].start
#                            #                                print "LCSP end ",play_tricks[rand_trick_command].end
#                            #                                print "LCSP runTime ",play_tricks[rand_trick_command].runTime
#                            #                                print "LCSP wait ",play_tricks[rand_trick_command].wait
#                            self.trickPlayArray[rand_thread].lock.notifyAll()
#                            #self.trickPlayArray[rand_thread].lock.notify()
#                            self.trickPlayArray[rand_thread].lock.release()
#                            tp_flip_flop[i] = 1
#                        if ff_flag == 0:
#                            self.trickPlayArray[old_thread].lock.release()
#                        else:
#                            self.trickPlayArray[trick_commands_array[i]].lock.release()
#                    else:
#                        #this is in order to show the dispatcher that threads have been catching the lock
#                        tp_flip_flop[i] = 0
#                time.sleep(0.001)
#                #print "<<<<<<<<<<<<<<<<<<<<<<<FINISHED setting %s TP>>>>>>>>>>>>>>" % (num_of_trick_commands)
#
#                delta_time = time.time() - begin_time
#                real_run_duration = orig_run_duration - delta_time
#
#            for i in range(len(self.threads)):
#                self.trickPlayArray[i].lock.acquire()
#                self.trickPlayArray[i].is_my_turn = 1
#                self.trickPlayArray[i].setLscp(self.lsc_tool_play_resume, "1", "NOW", "END", "5", "1")
#                self.trickPlayArray[i].lock.notifyAll()
#                self.trickPlayArray[i].lock.release()
#                #print "FINISHING THREAD No " , i
#            for i in range(len(self.threads)):
#                self.threads[i].join()
#
#            log2.debug(
#                "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Dispatcher # %s has ended >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" % (
#                self.dispatcher_serial))
#
#        else:
#            while (1):
#                delta_time = time.time() - begin_time
#                for i in range(num_of_trick_commands):
#                    if(self.trickPlayArray[trick_commands_array[i]].lock.acquire(0)):
#                        #print "after lock Status %s  for thread %s" % (str(trickPlayArray[trick_commands_array[i]].lock.locked()) , trick_commands_array[i])
#                        ff_flag = 1
#                        if tp_flip_flop[i] == 0:
#                            ff_flag = 0
#                            old_thread = trick_commands_array[i]
#                            rand_trick_command = random.randint(0, len(play_tricks) - 1)
#                            rand_thread = random.randint(0, len(self.threads) - 1)
#
#                            while(1):
#                                if self.trickPlayArray[rand_thread].lock.acquire(0):
#                                    if(self.trickPlayArray[rand_thread].is_my_turn != 1):
#                                        break
#                                    else:
#                                        self.trickPlayArray[rand_thread].lock.release()
#                                        rand_trick_command = random.randint(0, len(play_tricks) - 1)
#                                        rand_thread = random.randint(0, len(self.threads) - 1)
#                                else:
#                                    rand_trick_command = random.randint(0, len(play_tricks) - 1)
#                                    rand_thread = random.randint(0, len(self.threads) - 1)
#                            self.trickPlayArray[rand_thread].is_my_turn = 1
#                            trick_commands_array[i] = rand_thread
#                            #print "DISPATCHER  INDEX IS: ********************%s  in Array val %s " % (str(i) , str(trick_commands_array[i]) )
#                            #print "setting TP parameter for thread : %s" % (rand_thread)
#                            if self.command_duration < delta_time:
#                                real_command_duration = self.command_duration
#                            else:
#                                real_command_duration = delta_time
#
#                            real_command_duration *= 0.97
#                            #print "<<<<<<<<<<<<<<< Real Command Duration:" , real_command_duration
#                            #actual_TP_duration = int(int(self.command_duration) / abs(int(play_tricks[rand_trick_command].scale)))
#                            actual_TP_duration = int(
#                                int(real_command_duration) / abs(int(play_tricks[rand_trick_command].scale)))
#                            #print "<<<<<<<<<<<<<<< Actual Run Duration:" , actual_TP_duration
#                            if actual_TP_duration == 0:
#                                actual_TP_duration = 2
#                            if (play_tricks[rand_trick_command].mode == "U" and actual_TP_duration >= 60):
#                                # because after 60 sec PAUSE play out are torn down
#                                actual_TP_duration = 55
#                                #print "<<<<<<<<<<<<<<<< DISPATCHER set TP duration %s for scale %s " % (actual_TP_duration ,play_tricks[rand_trick_command].scale )
#                            self.trickPlayArray[rand_thread].setLscp(play_tricks[rand_trick_command].mode,
#                                play_tricks[rand_trick_command].scale, play_tricks[rand_trick_command].start,
#                                play_tricks[rand_trick_command].end, actual_TP_duration,
#                                play_tricks[rand_trick_command].wait)
#                            #                                print "LCSP mode " ,play_tricks[rand_trick_command].mode
#                            #                                print "LCSP scale  ",play_tricks[rand_trick_command].scale
#                            #                                print "LCSP start ",play_tricks[rand_trick_command].start
#                            #                                print "LCSP end ",play_tricks[rand_trick_command].end
#                            #                                print "LCSP runTime ",play_tricks[rand_trick_command].runTime
#                            #                                print "LCSP wait ",play_tricks[rand_trick_command].wait
#                            self.trickPlayArray[rand_thread].lock.notifyAll()
#                            #                                self.trickPlayArray[rand_thread].lock.notify()
#                            self.trickPlayArray[rand_thread].lock.release()
#                            tp_flip_flop[i] = 1
#                        if ff_flag == 0:
#                            self.trickPlayArray[old_thread].lock.release()
#                        else:
#                            self.trickPlayArray[trick_commands_array[i]].lock.release()
#                    else:
#                        tp_flip_flop[i] = 0
#                    delta_time = time.time() - begin_time
#                time.sleep(0.001)


#class Single_Thread(threading.Thread):
#    def __init__(self, command_duration, trick_play_percent, total_duration, loop_mode, Sessions_List,
#                 lsc_tool_play_resume, single_thread_socket,sessionsToHandle_lock, sessionsToHandle,
#                 no_delay_sessions, sec_delay_sessions, playoutMode, start_sessions_after_alloc):
#        threading.Thread.__init__(self)
#        self.trick_play_percent = trick_play_percent
#        self.command_duration = command_duration
#        self.total_duration = total_duration
#        self.loop_mode = loop_mode
#        self.Sessions_List = Sessions_List
#        self.lsc_tool_play_resume = lsc_tool_play_resume
#
#
#        self.sessionsToHandle_lock = sessionsToHandle_lock
#        self.sessionsToHandle = sessionsToHandle
#        self.single_thread_socket = single_thread_socket
#
#        self.no_delay_sessions = no_delay_sessions
#        self.sec_delay_sessions = sec_delay_sessions
#        self.start_sessions_after_alloc = start_sessions_after_alloc
#        self.playoutMode = playoutMode
#        self.running = True
#
#
#    def tearDownAllSessions(self):
#        for i in xrange(len(self.Sessions_List)):
#            self.Sessions_List[i].end_rtsp()
#        closed = 0
#        while(closed!=len(self.Sessions_List)):
#            closed = 0
#            for i in xrange(len(self.Sessions_List)):
#                if(self.Sessions_List[i].state == SessionStateEnum.CLOSED):
#                    closed+=1
#
#    def run(self):
#        log2 = logging.getLogger("Single Thread")
#        max_loops = 0
#        min_duration = 1000000
#
#        path = "../"
#        cfg = Globals.cfg
#        try:
#            tricks_file = open(path + "/" + "conf/trickplay.lscp", "r")
#        except IOError:
#            log2.critical("Trick file can not be found.\nScript finished")
#            sys.exit()
#        all_lines = tricks_file.readlines()
#        play_tricks = []
#
#        objs = "PT"
#        #elif cfg.lsc_tool_play_resume == "R"  :
#        #    objs = "RRU"
#        freqs = [int(100 - self.trick_play_percent), int(self.trick_play_percent)]
#        wc = wchoice(objs, freqs, filter=False)
#
#        tp_command = [wc() for _ in xrange(1000)]
#
#        play = DefObjects.lscpTricks('P', '1', 'NOW', 'END', '10', '1\n')
#        i = 0
#        for single_lines in all_lines:
#            line = str(single_lines).split(" ")
#            if line[0] == '#':
#                continue
#            trick = DefObjects.lscpTricks(line[0], line[1], line[2], line[3], line[4], line[5].rstrip())
#
#            #play_tricks - this is list containing all trick play commands
#            if(tp_command[i] == 'T'):
#                play_tricks.append(trick)
#            else:
#                play_tricks.append(play)
#
#            i += 1
#            if(i == 999):
#                i = 0
#
#        #sessions_num_of_loops = []
#        sessions_orig_run_duration = []
#        session_run_duration = []
#        for i in xrange(len(self.Sessions_List)):
#            if (self.total_duration != 0) and (int(self.total_duration) >= self.Sessions_List[i].duration):
#                if self.Sessions_List[i].duration != 0:
#                    runLength = int(int(self.total_duration) / self.Sessions_List[i].duration)
#                #                        print "<<<<<<<<<<>>>>>>>>>>>>> " + str(runLength)
#                else:
#                    runLength = 1
#            else:
#                runLength = 1
#
#            #sessions_num_of_loops.append(runLength)
#            if max_loops <= runLength:
#                max_loops = runLength
#
#            #how much time to run each loop!!
#            if float(self.total_duration) > self.Sessions_List[i].duration:
#                real_run_duration = self.Sessions_List[i].duration
#            else:
#                real_run_duration = self.total_duration
#
#            if min_duration >= int(real_run_duration):
#                min_duration = int(real_run_duration)
#
#            sessions_orig_run_duration.append(int(real_run_duration))
#            session_run_duration.append(int(real_run_duration))
#
#
#        allocThread = Session_Allocation_Thread(self.Sessions_List,self.single_thread_socket,self.no_delay_sessions)
#        allocThread.start()
#        if(self.start_sessions_after_alloc != 1):
#            allocThread.join()
#
#
#        begin_time = time.time()
#
#        for loop in xrange(max_loops):
#            for min_time_duration_counter in xrange(min_duration):
#                try:
#                    if(not self.running):
#                        raise SystemExit
#                    with self.sessionsToHandle_lock:
#                        for session in self.sessionsToHandle:
#                            if(session.state == SessionStateEnum.INIT):
#                                session.allocate()
#                            if(session.state == SessionStateEnum.DESCRIBE_RECEIVED):
#                                session.handle_rtsp_request(rtspVerbEnum.SETUP,session.setup_headers,session.setup_content)
#                                session.state = SessionStateEnum.SETUP_SENT
#                            if(session.state == SessionStateEnum.SETUP_RECEIVED):
#                                session.start(self.single_thread_socket)
#                            elif (session.state == SessionStateEnum.GET_PARAMETERS_RECEIVED):
#                                if(int(session.next_seek_jump) + session.posision >0):
#                                    session.rtsp_seek(int(session.next_seek_jump) + session.posision,self.single_thread_socket)
#                                else:
#                                    session.rtsp_seek(0,self.single_thread_socket)
#                            elif (session.state == SessionStateEnum.TEARDOWN_RECEIVED):
#                                session.alloc_rtsp_sess(self.single_thread_socket)
#                            elif (session.state == SessionStateEnum.ANNOUNCE_RECEIVED):
#                                session.rtsp_teardown()
#
#                        del self.sessionsToHandle[:]
#
#                    for i in xrange(len(self.Sessions_List)):
#                        current_time = time.time()
#                        rand_trick_command = random.randint(0, len(play_tricks) - 1)
#                        delta_current_time = current_time - begin_time
#                        if (int(delta_current_time < session_run_duration[i])) and self.trick_play_percent>0 and (
#                            int(self.Sessions_List[i].trick_duration) < int(current_time - self.Sessions_List[i].trick_init_time)):
#                            if(cfg.playoutMode !=PlayoutModeEnum.RTSP):
#                                self.Sessions_List[i].rtsp_trick_play(play_tricks[rand_trick_command].mode,
#                                    play_tricks[rand_trick_command].scale, play_tricks[rand_trick_command].start,
#                                    play_tricks[rand_trick_command].end, self.single_thread_socket)
#                            else:
#                                if(play_tricks[rand_trick_command].mode == "U" or play_tricks[rand_trick_command].scale == "1"):
#                                    self.Sessions_List[i].rtsp_trick_play(play_tricks[rand_trick_command].mode,
#                                        play_tricks[rand_trick_command].scale, play_tricks[rand_trick_command].start,
#                                        play_tricks[rand_trick_command].end, self.single_thread_socket)
#                                else:
#
#                                    self.Sessions_List[i].rtsp_get_parameters(self.single_thread_socket)
#                                    self.Sessions_List[i].next_seek_jump = play_tricks[rand_trick_command].scale
#
#                            self.Sessions_List[i].trick_init_time = time.time()
#
#                            real_command_duration = self.command_duration
#                            real_command_duration *= 0.97
#                            #print "<<<<<<<<<<<<<<< Real Command Duration:" , real_command_duration
#
#                            actual_TP_duration = int(
#                                int(real_command_duration) / abs(int(play_tricks[rand_trick_command].scale)))
#                            #print "<<<<<<<<<<<<<<< Actual Run Duration:" , actual_TP_duration
#                            if actual_TP_duration == 0:
#                                actual_TP_duration = 2
#
#                            if (play_tricks[rand_trick_command].mode == "U" and actual_TP_duration >= 60):
#                            # because after 60 sec PAUSE play out are torn down
#                                actual_TP_duration = 50
#                            self.Sessions_List[i].trick_duration = actual_TP_duration
#
#                        elif int(delta_current_time) < int(session_run_duration[i]) and (
#                            self.Sessions_List[i].trick_duration > int(current_time - self.Sessions_List[i].trick_init_time)):
#                            pass
#                        elif int(delta_current_time) > int(session_run_duration[i]):
#                            pass
##                            print "<<<<<<<<<<<<<<<<<<<<<<<<Tear Down Session:>>>>>>>>>>>>>>>>>>>>>> " + str(
##                                self.Sessions_List[i].session_id) + " <<<<< run duration >>>> " + str(
##                                int(session_run_duration[i])) + " >>>>>>>> delta time >>> " + str(
##                                int(delta_current_time))
##                            print "!!!!!!"
##
##                            session_run_duration[i] = sessions_orig_run_duration[i] + session_run_duration[i]
##
##                            self.Sessions_List[i].end_rtsp(self.single_thread_socket)
#
#
#
#                    time.sleep(0.3)
#
#                except Exception, e:
#                    Globals.failed_counter += 1
#                    print "EXIT WITH ERROR:", e
#                    if ((str(e).find("Broken pipe") != -1) or (str(e).find("Connection reset by peer") != -1) or (e.args[0] == 10053)):
#                        count = 0
#                        while(1):
#                            try:
#                                time.sleep(0.5)
#                                self.single_thread_socket.close()
#                                count += 1
#                                self.single_thread_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                                self.single_thread_socket.settimeout(None)
#                                self.single_thread_socket.connect(
#                                    (str(cfg.manager[:string.find(cfg.manager, ":")]).strip(), 554))
##                                self.sock_lock.acquire()
##                                self.replaced_socket.append(self.single_thread_socket)
##                                self.sock_lock.release()
#                                print "Replaced Socket in writer - retry: %s\n " % str(count)
#                                break
#                            except:
#                                pass
#                    if(isinstance(e,RTSP_Command_Err)):
#                        self.Sessions_List.remove(e.Session)
#
##        for i in range(len(self.Sessions_List)):
##            self.Sessions_List[i].end_rtsp(self.single_thread_socket)
##            self.single_thread_socket.close
##        return
#
#
#
#
#class Single_Thread_reader(threading.Thread):
#    def __init__(self, GlobalCseq,sessionsToHandle,sessionsToHandle_lock, networkService):
#        threading.Thread.__init__(self)
#        self.networkService = networkService
#        self.GlobalCseq = GlobalCseq
#        self.running = True
#        self.sessionsToHandle = sessionsToHandle
#        self.sessionsToHandle_lock = sessionsToHandle_lock
#
#    def __handle_describe__(self,msg,session):
#        session.state = SessionStateEnum.DESCRIBE_RECEIVED
#        if( "a" in msg.headers):
#            session.set_new_url(msg.headers["a"].replace("control:",""))
#
#
#        with self.sessionsToHandle_lock:
#            self.sessionsToHandle.append(session)
#
#
#    def __handle_setup__(self,msg,session):
#        if "Session" in msg.headers:
#            session.set_session_id(msg.headers["Session"])
#        else:
#            print "Error SETUP response contains no header - Session"
#        session.state = SessionStateEnum.SETUP_RECEIVED
#        with self.sessionsToHandle_lock:
#            self.sessionsToHandle.append(session)
#

#
#
#    def __handle_get_parameters__(self,msg,session):
#        session.posision = float(msg.headers["position"])
#        session.state = SessionStateEnum.GET_PARAMETERS_RECEIVED
#        with self.sessionsToHandle_lock:
#            self.sessionsToHandle.append(session)
#
#
#
#    def run(self):
#
#        while(self.running):
#            try:
#                session,messege = self.networkService.getNextMsg()
#                if(not Globals.parser.is_rtsp_response(messege)):
#                    pass
#                    packet = RTPDatagram(messege)
#                    print packet.SyncSourceIdentifier,packet.SequenceNumber
##                    print "this is a data packet"
#                else:
#                    msg  = Globals.parser.parse_rtsp_massages(messege)
#                    print msg[0]
#                    if(session.state == SessionStateEnum.DESCRIBE_SENT):
#                        self.__handle_describe__(msg[0],session)
#                    elif (session.state == SessionStateEnum.SETUP_SENT):
#                        if(msg[0].code == RTSPStatusCodeEnum.OK):
#                            self.__handle_setup__(msg[0],session)
#                        elif(msg[0].code == RTSPStatusCodeEnum.MOVED_TEMPORARILY or msg[0].code == RTSPStatusCodeEnum.MOVED_PERMANENTLY):
#                            self.__handle_redirect__(msg[0],session)
#                            session.state = SessionStateEnum.DESCRIBE_RECEIVED
#                            with self.sessionsToHandle_lock:
#                                self.sessionsToHandle.append(session)
#                        else:
#                            self.__handle_error__()
#                    elif (session.state == SessionStateEnum.TEARDOWN_SENT):
#                        if(msg[0].code == RTSPStatusCodeEnum.OK):
#                            if(not session.CloseSession):
#                                session.state = SessionStateEnum.INIT
#                                with self.sessionsToHandle_lock:
#                                    self.sessionsToHandle.append(session)
#                            else:
#                                session.state = SessionStateEnum.CLOSED
#                        elif(msg[0].code == RTSPStatusCodeEnum.MOVED_TEMPORARILY or msg[0].code == RTSPStatusCodeEnum.MOVED_PERMANENTLY):
#                            self.__handle_redirect__(msg[0],session)
#                            session.state = SessionStateEnum.ANNOUNCE_RECEIVED
#                            with self.sessionsToHandle_lock:
#                                self.sessionsToHandle.append(session)
#
#
#
#                time.sleep(0.01)
#                recv_buffer = None
#            except Exception ,e:
#                if(isinstance(e,TypeError)):
#
#                    time.sleep(0.01)
#                else:
#                    print e
#
#    def __handle_error__(self):
#        pass


                

                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                