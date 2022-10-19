import os
import threading
import sys
import time
from ConfigReader import cfg
from Parser import Parser
from Manager import Manager
from definitions.TrickPlayMixer import TrickPlayMixer


def timed_func(method,*params):
    time_before = time.time()
    response = method(params[0])
    time_after = time.time()
    total_time = time_after - time_before

    return total_time,response


def banner_msg(msg,level,log):

    message ="\n"+"*"*(len(msg)+4) + "\n* " + msg + " *\n" + "*"*(len(msg)+4)
    if(str(level).upper() == "DEBUG"):
        log.debug(message)
    elif (str(level).upper() == "INFO"):
        log.info(message)
    elif (str(level).upper() == "ERROR"):
        log.error(message)
    elif (str(level).upper() == "WARNING"):
        log.warning(message)


def calculate_sleep_time(scale,asset_duration,current_position):
    if scale>0:
        to_edge =  ((float(asset_duration) - float(current_position))/int(scale))/1000
        print str( "to_edge " +str(to_edge)  + " with scale " + str(scale) +  " from " + str(current_position) + " to " + str(asset_duration) )
    elif scale<0:
        if(float(current_position)<1000):
            current_position = float(asset_duration)/2
        to_edge = -(float(current_position)/int(scale))/1000
        print str( "to_edge " +str(to_edge)  + " with scale " + str(scale) +  " from " + str(current_position) + " to 0" )
    else:
        return 55

    if(to_edge<cfg.command_duration):
        return to_edge
    else:
        return (cfg.command_duration)/scale



def manager_ip():
    return cfg.manager


def machine_64_bit():
    return cfg.machine_64bit


def LSC_transport_layer():
    return cfg.LSC_Transport_Layer


def checkByxPath(dom, xpath):
    r=None
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content

    return r



path = os.getcwd()
srcPath = "%s%s" % (path, "/src")
sys.path.append(srcPath)

parser = Parser()



#   object of all configuration parameters



def init_manager():
    return  Manager(cfg.manager,cfg.enable_ssl,cfg)


managerObj = None
trickplay_mixer = TrickPlayMixer(cfg,parser)
print "globals import"

global_lock = threading.Lock()
success_counter = 0
failed_counter = 0
alloc_list = []
playout_mode = 0
isSSL = 0

act_lscp_stat = 0
lscp_stat_dly = 1

mainPath = ""

# Checking the Manager version











