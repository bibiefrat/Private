
from definitions import Logger, color
from ConfigReader import cfg
from model.ABR import get_rolling_buffers_as_assets

Logger.defineLogger(cfg.log_file, cfg.desired_log_level)



import py_compile

from Manager import Manager
from NetworkService import NetworkService, SendingThreadPool
from Parser import Parser
import os
import sys

from definitions.DefObjects import PlayoutModeEnum
from model import SessionManager


from model.RTSP import GlobalCseq
from titles import OpenTitle
from RandomThread import *


import string
import random

py_compile.compile("Playout.py")


VERSION = "1.0"

path = "../"
srcPath = "%s%s" % (path, "src")
sys.path.append(srcPath)




def create_lscp_file():
    objs = "PRU"
    freqs = [int(cfg.ff_percent), int(cfg.rew_percent), int(cfg.pause_percent)]
    wc = wchoice(objs, freqs, filter=False)
    tp_command = [wc() for _ in xrange(1000)]
    ff_scales = [2, 4, 7, 8, 12, 16, 24, 30, 32, 36, 60, 120]
    rew_scales = [-2, -4, -7, -8, -12, -16, -24, -30, -32, -36, -60, -90]
    ff_seek = [300,30]
    rew_seek =  [-300,-30]

    path = "../"
    lscp_file = open(path + "conf/" + "trickplay.lscp", "w")
    if(cfg.playout_mode != PlayoutModeEnum.RTSP):
        lscp_file.write("# mode scale start_npt stop_npt runTime wait\n")
        if cfg.lsc_tool_play_resume == 'P':
            for i in range(1000):
                if tp_command[i] == 'P':
                    scale = str(random.choice(ff_scales))
                    lscp_file.write("P %s NOW END 10 0\n" % (scale))
                elif tp_command[i] == 'R':
                    scale = str(random.choice(rew_scales))
                    lscp_file.write("P %s NOW 0 10 0\n" % (scale))
                else:
                    scale = "0"
                    lscp_file.write("U %s NOW NOW 10 0\n" % (scale))

        elif cfg.lsc_tool_play_resume == 'R':
            for i in range(1000):
                if tp_command[i] == 'P':
                    scale = str(random.choice(ff_scales))
                    lscp_file.write("R %s NOW END 10 0\n" % (scale))
                elif tp_command[i] == 'R':
                    scale = str(random.choice(rew_scales))
                    lscp_file.write("R %s NOW 0 10 0\n" % (scale))
                else:
                    scale = "0"
                    lscp_file.write("U %s NOW NOW 10 0\n" % (scale))
    else:
        lscp_file.write("# mode seek start_npt stop_npt runTime wait\n")
        for i in range(1000):
            if tp_command[i] == 'P':
                seek = str(random.choice(ff_seek))
                lscp_file.write("P %s NOW END 10 0\n" % (seek))
            elif tp_command[i] == 'R':
                seek = str(random.choice(rew_seek))
                lscp_file.write("P %s NOW 0 10 0\n" % (seek))
            else:
                seek = str(random.choice(ff_seek))
                lscp_file.write("U %s NOW NOW 10 0\n" % (seek))
    lscp_file.close()








def defineReporter():
    # Defining the log for report file !

    formatter = logging.Formatter("[%(asctime)-19s] %(name)-8s: %(message)26s", datefmt='%d-%m-%Y %H:%M:%S')

    console = logging.FileHandler(path + "/log/report.log", 'w')
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    report = logging.getLogger('REPORT')
    report.addHandler(console)

    return report


def stb_ip_parse(ip):
    ipNums = ip.split('.')
    return ipNums[0:4]








def CreateAllSessions( numOfSessions,  sessionManager):

    #global Sessions_List
    global numSess
    global playlists_index

    numOfSessions += numSess - 1

    while numSess <= numOfSessions:
        sessionManager.AddSession()
        numSess += 1





def calc_alloc_time():
    total_alloc_time = float(0)
    list_length = len(Globals.alloc_list)

    if list_length > 0:
        for i in range(list_length):
            total_alloc_time = total_alloc_time + Globals.alloc_list[i]
        avg_alloc_time = float(total_alloc_time / list_length)
        min_alloc = min(Globals.alloc_list)
        max_alloc = max(Globals.alloc_list)

        print "AVG time of alloc = %.3f , min alloc time = %.3f, max alloc time = %.3f " % (
        avg_alloc_time, min_alloc, max_alloc)
    else:
        print color_loc.render('${RED}No assets were played, therefore no allocation was done. ${NORMAL}')


def report():
    report = defineReporter()

    print color_loc.render('${BLUE} REPORT ${NORMAL}')
    report.critical("\n\n\n" + ('*' * 20))
    report.critical("\t\t$$$$$$$$$$$ Test report: $$$$$$$$$$$")
    report.critical("\t\t   Total of Successful sessions = " + str(Globals.success_counter))
    report.critical("\t\t   Total of Failed sessions = " + str(Globals.failed_counter))
    report.critical("\t\t$$$$$$$$$$$ End of report $$$$$$$$$$$")
    if cfg.print_alloc_time == 1:
        calc_alloc_time()


def global_init():
    Globals.managerObj =  Manager(cfg.manager, cfg.enable_ssl, cfg)
    Globals.isSSL = cfg.enable_ssl
    Globals.playout_mode = cfg.playout_mode
    Globals.mainPath = path
    Globals.act_lscp_stat = cfg.lscp_status
    Globals.lscp_stat_dly = cfg.stat_delay




log = logging.getLogger('Main')




try:


    print "running on "  + os.name
    global_init()
    #Getting the process ID of the playout script
    pid_num = os.getpid()
    #print "pid = " + str(pid_file)
    X = os.system('echo %s > pid.txt' % (pid_num))
    # printing Script Title    
    OpenTitle.opTitle()
    single_thread_socket = None
    path = "../"
    cfg = Globals.cfg
    cfg.asset_list_path = path + cfg.asset_list_path
    logging.getLogger("").info("playout script started " + "*"*10)
    if(int(cfg.create_asset_list) == 1 ):
        p = get_rolling_buffers_as_assets()
#        random.shuffle(p)
        dump = open("../conf/AbrAutoList.txt", mode="w+")
        dump.writelines([str(x) + "\n" for x in p])
        dump.close()
        exit()
#    networkService = NetworkService()
    networkService = NetworkService()

#    sendingThread = SendingThread(networkService)
#    sendingThread.start()
    sendingThread = SendingThreadPool(networkService,cfg.number_of_sending_threads)

    sessionManager = SessionManager(networkService,sendingThread)




    # creating parser
    parser = Parser()


    if cfg.playout_mode != PlayoutModeEnum.HTTP:
        tricks_params = parser.lscp_tricks(cfg.trickplay_list_path, path)
    else:
        tricks_params = parser.parse_trickPlays(cfg.trickplay_list_path, path)


    playlists_index = 0
    numSess = 1


    # MAX max session duration
    max_ses_duration = 0

    color_loc = color.TerminalController()



    #create LSCP file
    if cfg.trick_play_percent > 0:
        create_lscp_file()


#    real_stbs_list = cfg.real_stb.split(';')
#    num_real_sessions_list1 =str(cfg.num_real_session).split(";")
#    num_real_sessions_list = [int(i) for i in cfg.num_real_session.split(';')[:len(real_stbs_list)]]

    #dispatcher_serial = 0
    GlobalCseq = GlobalCseq()


    while (1):
        trickPlayArray = []
        threads = []

        manager_version = Globals.managerObj.get_manager_version()
        version_num = stb_ip_parse(manager_version)

        networkService.start()
        sessionManager.start()

        CreateAllSessions(cfg.total_sessions,   sessionManager)

        while(1):
            ans = string.lower(raw_input("Would you like to add more sessions? \n"))
            if(ans.startswith("+")):
                num = int(ans[1:])
                for x in xrange(num):
                    sessionManager.AddSession()
            if(ans == "n"):

                sys.exit()
                break
            elif(ans == "t"):
                print "TEARDOWN !!!"

                sys.exit()

        break

except KeyboardInterrupt:
    print "Exit main by ctrl-c"


    report()

    try:
        pid_file = open("pid.txt", "r")
        pid_num = pid_file.read()
        Y = os.system('kill -9 %s' % (pid_num))
        Z = os.system('rm -f pid.txt')
    except:
        "Error while trying to kill the playout script"
        pass
except SystemExit, e:
    #print "doing tear_down for all sessions"

    try:
        print "!!!!!!!"
        pid_file = open("pid.txt", "r")
        pid_num = pid_file.read()
        Y = os.system('kill -9 %s' % (pid_num))
        Z = os.system('rm -f pid.txt')
        sys.exit(0)
    except:
        print "Error while trying to kill the playout script"

        sys.exit(0)


#except Exception, e:
#    print e
#    log.error(e)
#    #sys.exit(0)
#    try:
#        pid_file = open("pid.txt", "r")
#        pid_num = pid_file.read()
#        Y = os.system('kill -9 %s' % (pid_num))
#        Z = os.system('rm -f pid.txt')
#    except:
#        "Error while trying to kill the playout script"
#        pass

report()
#sys.exit(0)
try:
    pid_file = open("pid.txt", "r")
    pid_num = pid_file.read()
    Y = os.system('kill -9 %s' % (pid_num))
    Z = os.system('rm -f pid.txt')
except:
    "Error while trying to kill the playout script"
    pass
