import os
from logging import Logger

import string
import sys
import urllib
import urllib2
import libxml2
import socket
from definitions import Globals
from Parser import *
from FxThread import *
import time
import logging
import signal

from definitions import  SessExceptions

#path = os.getcwd()
path = "../"
srcPath = "%s%s" % (path, "/src")

sys.path.append(srcPath)


def signal_handler(signal, frame):
    raise SystemExit


def defineLogger():
    # Defining the log level and handling
    print cfg.desired_log_level
    log_level = string.upper(cfg.desired_log_level)
    print "Log level = " + log_level
    if log_level == "DEBUG":
        log_print = logging.DEBUG
    elif log_level == "INFO":
        log_print = logging.INFO
    elif log_level == "WARNING":
        log_print = logging.WARNING
    elif log_level == "ERROR":
        log_print = logging.ERROR
    elif log_level == "CRITICAL":
        log_print = logging.CRITICAL

#    formatter = logging.Formatter(
#        "[%(asctime)s] %(name)-8s: [%(levelname)s] %(message)26s")#, datefmt='%d-%m-%Y %H:%M:%S')
#    logging.basicConfig(level=log_print,
#        format="[%(asctime)s] %(name)-8s: [%(levelname)s] %(message)26s",
        #datefmt='%d-%m-%Y %H:%M:%S',
 #       filename=path + "/" + cfg.log_file,
 #       filemode='w')
    console = logging.StreamHandler()
    console.setLevel(log_print)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    signal.signal(signal.SIGINT, signal_handler)


def defineReporter():
    # Defining the log for report file !

    formatter = logging.Formatter("[%(asctime)s] %(name)-8s: %(message)26s")#, datefmt='%d-%m-%Y %H:%M:%S')

    console = logginfx_idg.FileHandler(path + "/log/report.log", 'w')
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    report = logging.getLogger('REPORT')
    report.addHandler(console)

    return report


def streamers_sessions(streamer_ip):
    global num_of_session_per_sec_fast_mode
    global TearDownPerSec
    parse_sessions_list = None
    try:
        try:
            sessions_url = "http://%s/command/monitor_service?id=SESSIONS_IDS&opaque=" % (streamer_ip)
            print "sessions_url = " + str(sessions_url)
            sessions_result = urllib2.urlopen(sessions_url)
            xml_sessions_list = sessions_result.read()
            parse_sessions_list = libxml2.parseDoc(xml_sessions_list)
            zero_sessions = checkByxPath(parse_sessions_list, "//X/size")
            print " Streamer %s : " % (streamer_ip)
            if zero_sessions == "0":
                print "   No open sessions on streamer .\n"
            else:
                print "   Total allocated sessions = %s . \n" % (zero_sessions)
                if (TearDownPerSec == 0):
                    total_sessions_list = Sessions_id_ByxPath(parse_sessions_list, "//X/elem/session_id/",
                        num_of_session_per_sec_fast_mode)
                else:
                    Sessions_Accumulation(parse_sessions_list, "//X/elem/session_id/")
        except:
            print "Error reading open sessions from streamer : %s \n" % (streamer_ip)
            pass
    finally:
        if parse_sessions_list:
            parse_sessions_list.freeDoc()


def Sessions_Accumulation(dom, xpath):
    global accumulated_list
    global accumulated_list_type_numeric
    global accumulated_list_type_dsmcc
    #fxIDStr = xpath + "fx_id"


    fxIDStr = "//X/elem/session_id/fx_id"
    list = dom.xpathEval(fxIDStr)
    for url in list:
        accumulated_list.append(str(url.content))

    fxIDStr = "//X/elem/session_id/numeric_id"
    list = dom.xpathEval(fxIDStr)
    for url in list:
        accumulated_list_type_numeric.append(str(url.content))

    fxIDStr = "//X/elem/session_id/dsmcc_id"
    list = dom.xpathEval(fxIDStr)
    for url in list:
        accumulated_list_type_dsmcc.append(str(url.content))

    fxIDStr = "//X/elem/session_id_string"
    list = dom.xpathEval(fxIDStr)
    for url in list:
        accumulated_list_type_string.append(str(url.content))

    return accumulated_list


def Session_Deletion(TearDownPerSec):
    ############## batch Delete ##########################
    log2 = logging.getLogger("TearDown")
    global accumulated_list
    global accumulated_list_type_numeric
    global accumulated_list_type_dsmcc
    global num_of_deletion
    global accumulated_list_type_string


    #IF not in LSCP mode in the ini file -> NOT using rtsp plugin
    if (isLSCP != 2 and isLSCP != 6):
        batch_counter = 0
        time_before_batch = int(((time.time() * 1000)))

        #for url in accumulated_list:
        #    r = url.content
        for r in accumulated_list:
            #r = url.content
            #print "r = " + str(r)           
            if (batch_counter == TearDownPerSec):
                time_after_batch = int(((time.time() * 1000)))
                #print "Time After Batch******** " , time_after_batch
                diff_time = time_after_batch - time_before_batch
                if (diff_time < 1000):
                    print "\n********* Batch of %d Tear Downs was performed during %d MiliSec *********" % (
                    TearDownPerSec, diff_time)
                    time.sleep(float(1000 - diff_time) / 1000.)
                else:
                    print "\n********** Batch TearDown of %d took More than 1000 MiliSec *********" % (TearDownPerSec)
                time_before_batch = int(((time.time() * 1000)))
                #print "Time Before Batch******** " , time_before_batch     
                batch_counter = 0
            try:
                url = "%s%s/mng_session_teardown?type=1&fx_id=%s" % (
                    Globals.managerObj.getHTTP(), manager, (urllib.quote_plus(str(r))))
                #print "url -->" + str(url)
                #log2.debug("      Running teardown for session ID = %s " % (urllib.quote_plus(str(r))))
                #print "      Running teardown for session ID = %s " % (urllib.quote_plus(str(r)))
                p = os.system("wget -b -q -o /dev/null  \"%s \" 1>/dev/null " % (url))
                if (p == 0):
                    num_of_deletion += 1
                else:
                    raise SessExceptions.tear_down__err((urllib.quote_plus(str(r))), "Session Tear Down Failed")

            except OSError:
                print "error on url = " + str(url)
                pass
            batch_counter += 1

        batch_counter = 0
        time_before_batch = int(((time.time() * 1000)))
        for r in accumulated_list_type_dsmcc:
            #r = url.content
            #print "r = " + str(r)           
            if (batch_counter == TearDownPerSec):
                time_after_batch = int(((time.time() * 1000)))
                #print "Time After Batch******** " , time_after_batch
                diff_time = time_after_batch - time_before_batch
                if (diff_time < 1000):
                    print "\n********* Batch of %d Tear Downs was performed during %d MiliSec *********" % (
                    TearDownPerSec, diff_time)
                    time.sleep(float(1000 - diff_time) / 1000.)
                else:
                    print "\n********** Batch TearDown of %d took More than 1000 MiliSec *********" % (TearDownPerSec)
                time_before_batch = int(((time.time() * 1000)))
                #print "Time Before Batch******** " , time_before_batch     
                batch_counter = 0
            try:
                url = "%s%s/mng_session_teardown?type=0&dsmcc_id=%s" % (
                    Globals.managerObj.getHTTP(), manager, (urllib.quote_plus(str(r))))
                #print "url -->" + str(url)
                #log2.debug("      Running teardown for session ID = %s " % (urllib.quote_plus(str(r))))
                #print "      Running teardown for session ID = %s " % (urllib.quote_plus(str(r)))
                p = os.system("wget -b -q -o /dev/null  \"%s\" 1>/dev/null " % (url))
                if (p == 0):
                    num_of_deletion += 1
                else:
                    raise SessExceptions.tear_down__err((urllib.quote_plus(str(r))), "Session Tear Down Failed")

            except OSError:
                print "error on url = " + str(url)
                pass
            batch_counter += 1

        batch_counter = 0
        time_before_batch = int(((time.time() * 1000)))

        #for url in accumulated_list_type_numeric:
        #    r = url.content
        for r in accumulated_list_type_numeric:
        #    r = url.content
            #print "r = " + str(r)           
            if (batch_counter == TearDownPerSec):
                time_after_batch = int(((time.time() * 1000)))
                #print "Time After Batch******** " , time_after_batch
                diff_time = time_after_batch - time_before_batch
                if (diff_time < 1000):
                    print "\n********* Batch of %d Tear Downs was performed during %d MiliSec *********" % (
                    TearDownPerSec, diff_time)
                    time.sleep(float(1000 - diff_time) / 1000.)
                else:
                    print "\n********** Batch TearDown of %d took More than 1000 MiliSec *********" % (TearDownPerSec)
                time_before_batch = int(((time.time() * 1000)))
                #print "Time Before Batch******** " , time_before_batch     
                batch_counter = 0
            try:
                url = "%s%s/mng_session_teardown?type=2&numeric_id=%s" % (
                    Globals.managerObj.getHTTP(), manager, (urllib.quote_plus(str(r))))
                #print "url -->" + str(url)
                #log2.debug("      Running teardown for session ID = %s " % (urllib.quote_plus(str(r))))
                #print "      Running teardown for session ID = %s " % (urllib.quote_plus(str(r)))
                p = os.system("wget -b -q -o /dev/null  \"%s \" 1>/dev/null " % (url))
                if (p == 0):
                    num_of_deletion += 1
                else:
                    raise SessExceptions.tear_down__err((urllib.quote_plus(str(r))), "Session Tear Down Failed")

            except OSError:
                print "error on url = " + str(url)
                pass
            batch_counter += 1








            #IF in LSCP mode in the ini file -> using rtsp plugin
    else:
        session_counter = 0
        batch_counter = 0
        time_before_batch = int(((time.time() * 1000)))
        rtsp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        onlyManager = manager[:string.find(manager, ":")]
        #print onlyManager
        rtsp_sock.connect((str(onlyManager).strip(), 554))
        #for url in accumulated_list_type_numeric:
        #    r = url.content

        if (isLSCP == 2 ):
            if is_numeic_session_id == 1:
                acc_list = accumulated_list_type_numeric
            else:
                acc_list = accumulated_list_type_string
            #	    acc_list = acc_list + accumulated_list_type_numeric + accumulated_list_type_string
        elif (isLSCP == 6 ):
            acc_list = accumulated_list_type_string
        for r in acc_list:
            #r = url.content
            #print "r = " + str(r)           
            if (batch_counter == TearDownPerSec):
                time_after_batch = int(((time.time() * 1000)))
                #print "Time After Batch******** " , time_after_batch
                diff_time = time_after_batch - time_before_batch
                if (diff_time < 1000):
                    print "\n********* Batch of %d Tear Downs was performed during %d MiliSec *********" % (
                    TearDownPerSec, diff_time)
                    time.sleep(float(1000 - diff_time) / 1000.)
                else:
                    print "\n********** Batch TearDown of %d took More than 1000 MiliSec *********" % (TearDownPerSec)
                time_before_batch = int(((time.time() * 1000)))
                #print "Time Before Batch******** " , time_before_batch     
                batch_counter = 0
            try:
                if (isLSCP == 2 ):
                    arg1 = "CSeq: 1"
                    arg2 = "Session: %s" % (str.strip(str(r)))
                    write_buffer = "TEARDOWN * RTSP/1.0\r\n%s\r\n%s\r\n\r\n" % (arg1, arg2)
                    print write_buffer
                elif (isLSCP == 6):
                    write_buffer = '''TEARDOWN rtsp://%s:554 RTSP/1.0
Ondemandsessionid: %s
Cseq: 1
Session: 1
Require: com.comcast.ngod.r2
Content-type: application/sdp

''' % (str(onlyManager), str.strip(str(r)))
                print    write_buffer
                sent = rtsp_sock.send(write_buffer)
                session_counter += 1            
                #recv_buffer = rtsp_sock.recv(8192)
                #print recv_buffer
            except OSError:
                pass
            batch_counter += 1
        number_of_teardown_sent = session_counter
        
        print ">>>>>>>>>>>>>>>>>>>>>>>" + str(session_counter)
        
        success_counter = 0
        recv_buffer = 'x'
        while (session_counter != 0 and len(recv_buffer)>0 ):
            recv_buffer = rtsp_sock.recv(8192 * 4)
            success_counter += recv_buffer.count("200 OK")
            session_counter -= recv_buffer.count("RTSP/1.0")
            print session_counter
            time.sleep(0.1)
            print recv_buffer

        rtsp_sock.close()
        num_of_deletion += success_counter
        if (number_of_teardown_sent != success_counter):
            print "<<<<<<<<<<<<<<<<<<<<<<<<<<< ERROR - Not All Session were torn down !!!!!!!!!!!! >>>>>>>>>>>>>>>>>>>>>"

        #    if ((TearDownPerSec - batch_counter != 0) and (len(accumulated_list) != 0 )):
        #        time_after_batch = int(((time.time()*1000)))
        #        diff_time =  time_after_batch - time_before_batch
        #        print "\n********* Batch of %d Tear Downs was performed during %d MiliSec *********" % (batch_counter ,diff_time)
        #

    return


def Sessions_id_ByxPath(dom, xpath, TearDownPerSec):
    log1 = logging.getLogger("TearDown")
    global num_of_deletion
    global lock

    #IF not in LSCP mode in the ini file -> NOT using rtsp plugin
    if (isLSCP != 2 and isLSCP != 6):
        time_before_batch = int(((time.time() * 1000)))
        #SleepBetweenTearDown = int(1000/TearDownPerSec)
        #fxIDStr = xpath + "fx_id"
        fxIDStr = "//X/elem/session_id/fx_id"
        list = dom.xpathEval(fxIDStr)
        batch_counter = 0
        #print "list = " + str(list[0])

        #print "Time Before Batch******** " , time_before_batch
        for url in list:
            r = url.content
            #print "r = " + str(r)           
            if (batch_counter == TearDownPerSec):
                time_after_batch = int(((time.time() * 1000)))
                #print "Time After Batch******** " , time_after_batch
                diff_time = time_after_batch - time_before_batch
                if (diff_time < 1000):
                    #print "<<<<<<< Batch of %d Tear Downs was performed during %d MiliSec >>>>>>>>" % (TearDownPerSec ,diff_time)
                    time.sleep(float(1000 - diff_time) / 1000.)
                else:
                    print "<<<<<<<<< Batch TearDown of %d took More than 1000 MiliSec >>>>>>>>" % (TearDownPerSec)
                time_before_batch = int(((time.time() * 1000)))
                #print "Time Before Batch******** " , time_before_batch     
                batch_counter = 0
            try:
            #time.sleep(0.001);
                url = "%s%s/mng_session_teardown?type=1&fx_id=%s" % (
                    Globals.managerObj.getHTTP(), manager, (urllib.quote_plus(str(r))))
                #print "url -->" + str(url) + "\n"
                log1.debug("      Running teardown for session ID = %s " % (urllib.quote_plus(str(r))))
                #print "      Running teardown for session ID = %s " % (urllib.quote_plus(str(r)))
                p = os.system("wget -q -b -o/dev/null  \"%s\" 1>/dev/null " % (url))
                lock.acquire()
                num_of_deletion += 1
                lock.release()
            except:
                print "error on url = " + str(url)
                pass
            batch_counter += 1

        time_before_batch = int(((time.time() * 1000)))
        #SleepBetweenTearDown = int(1000/TearDownPerSec)
        #fxIDStr = xpath + "fx_id"
        fxIDStr = "//X/elem/session_id/numeric_id"
        list = dom.xpathEval(fxIDStr)
        batch_counter = 0

        for url in list:
            r = url.content
            #print "r = " + str(r)           
            if (batch_counter == TearDownPerSec):
                time_after_batch = int(((time.time() * 1000)))
                #print "Time After Batch******** " , time_after_batch
                diff_time = time_after_batch - time_before_batch
                if (diff_time < 1000):
                    #print "<<<<<<< Batch of %d Tear Downs was performed during %d MiliSec >>>>>>>>" % (TearDownPerSec ,diff_time)
                    time.sleep(float(1000 - diff_time) / 1000.)
                else:
                    print "<<<<<<<<< Batch TearDown of %d took More than 1000 MiliSec >>>>>>>>" % (TearDownPerSec)
                time_before_batch = int(((time.time() * 1000)))
                #print "Time Before Batch******** " , time_before_batch     
                batch_counter = 0
            try:
            #time.sleep(0.001);
                url = "%s%s/mng_session_teardown?type=2&numeric_id=%s" % (
                    Globals.managerObj.getHTTP(), manager, (urllib.quote_plus(str(r))))
                #print "url -->" + str(url)
                log1.debug("      Running teardown for session ID = %s " % (urllib.quote_plus(str(r))))
                #print "      Running teardown for session ID = %s " % (urllib.quote_plus(str(r)))
                p = os.system("wget -q -b -o/dev/null  \"%s\" 1>/dev/null " % (url))
                lock.acquire()
                num_of_deletion += 1
                lock.release()
            except:
                print "error on url = " + str(url)
                pass
            batch_counter += 1

    #IF in LSCP mode in the ini file -> using rtsp plugin        
    else:
        session_counter = 0

        time_before_batch = int(((time.time() * 1000)))
        if (isLSCP == 2):
            if is_numeic_session_id == 1:
                fxIDStr = "//X/elem/session_id/numeric_id"
            else:
                fxIDStr = "//X/elem/session_id_string"
            list = dom.xpathEval(fxIDStr)
        elif (isLSCP == 6):
            fxIDStr = "//X/elem/session_id_string"
            list = dom.xpathEval(fxIDStr)
            #batch_counter = 0
        rtsp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        onlyManager = manager[:string.find(manager, ":")]
        #print onlyManager
        rtsp_sock.connect((str(onlyManager).strip(), 554))

        for url in list:
            r = url.content
            #print "r = " + str(r)           
            #            if (batch_counter == TearDownPerSec):
            #                time_after_batch = int(((time.time()*1000)))
            #                #print "Time After Batch******** " , time_after_batch
            #                diff_time =  time_after_batch - time_before_batch
            #                if (diff_time < 1000):
            #                    #print "<<<<<<< Batch of %d Tear Downs was performed during %d MiliSec >>>>>>>>" % (TearDownPerSec ,diff_time)
            #                    time.sleep(float(1000 - diff_time)/1000.)
            #                else:
            #                    print "<<<<<<<<< Batch TearDown of %d took More than 1000 MiliSec >>>>>>>>" %  (TearDownPerSec)
            #                time_before_batch = int(((time.time()*1000)))
            #                #print "Time Before Batch******** " , time_before_batch
            #                batch_counter = 0;
            #
            #
            if (isLSCP == 2):
                arg1 = "CSeq: 1"
                arg2 = "Session: %s" % (str.strip(str(r)))
                write_buffer = 'TEARDOWN * RTSP/1.0\r\n%s\r\n%s\r\n\r\n' % (arg1, arg2)
            elif (isLSCP == 6):
                write_buffer = '''TEARDOWN rtsp://%s:554 RTSP/1.0
Ondemandsessionid: %s
Cseq: 1
Session: 1
Require: com.comcast.ngod.r2
Content-type: application/sdp

''' % (str(onlyManager), str.strip(str(r)))
            print write_buffer

            sent = rtsp_sock.send(write_buffer)
            session_counter += 1
            #batch_counter += 1
        number_of_teardown_sent = session_counter
        success_counter = 0
        while (session_counter != 0):
            recv_buffer = rtsp_sock.recv(8192)
            success_counter += recv_buffer.count("200 OK")
            session_counter -= recv_buffer.count("RTSP/1.0")
            time.sleep(0.1)
            print recv_buffer
        rtsp_sock.close()
        lock.acquire()
        num_of_deletion += success_counter
        lock.release()
        if (number_of_teardown_sent != success_counter):
            print "<<<<<<<<<<<<<<<<<<<<<<<<<<< ERROR - Not All Session were torn down !!!!!!!!!!!! >>>>>>>>>>>>>>>>>>>>>"
    return


def checkByxPath(dom, xpath):
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content

    return r


def StreamerByxPath(dom, xpath):
    global StreamerID,cfg
    streamer_id_xpath = "//X/config/edges/elem/streamers/elem/id"
    streamer_id_list = dom.xpathEval(streamer_id_xpath)
    if StreamerID == 0:
        list = dom.xpathEval(xpath)
        for url in list:
            r = url.content
            r=r[:str.find(r,":")]+ ":" + str(cfg.streamer_port)
            streamers.append("%s" % (r))

        return
    else:
        streamer = str(StreamerID).split(';')
        for url in streamer_id_list:
            r = url.content                    
            for i in range(len(streamer)):
                if r == str(streamer[i]):
                    streamer_temp = ("%s" % (url.next.next.next.next.content))
                    streamer_temp=streamer_temp[:str.find(streamer_temp,":")]+ ":" + streamer_temp[str.rfind(streamer_temp,":")+1:]
                    #streamer=streamer[:str.find(streamer,":")]+ ":" + str(cfg.streamer_port)
                    streamers.append("%s" % (str(streamer_temp)))
                    
                    
                    
def del_from_db():
    global cfg
    teardown_session_modes=cfg.teardown_session_mode
    teardown_session_modes = teardown_session_modes.split(';')
    session_modes_to_teardown = ''
    for i in teardown_session_modes:
        session_modes_to_teardown +=i
        session_modes_to_teardown +=','
    session_modes_to_teardown = session_modes_to_teardown[:str.rfind(session_modes_to_teardown,",")]
    
    
    if cfg.db_type == "solid" :
        x = '''expect -c "set timeout -1;
        spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \' select session_id from session_state where mode in (%s) and done=0' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
        match_max 100000;
        expect *password:*;
        send -- %s\\r;
        interact;" | tr -d ' ' | sed '/^\s*$/d' | grep -v "spawn\|sess\|passwo\|---\|rows"   > sessions.list'''  % (str(db_addr),str(session_modes_to_teardown),str(db_machine_password))
        print x
        try:
            os.system(x)
        except:
            traceback.print_exc(file=sys.stdout)  
    else:
        x = '''expect -c "set timeout -1;
        spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \' select session_id from session_state where mode in (%s) and done=0';sleep 1 \); done; exit;\\";
        match_max 100000;
        expect *password:*;
        send -- %s\\r;
        interact;" | tr -d ' ' | sed '/^\s*$/d' | grep -v "spawn\|sess\|passwo\|---\|rows"  > sessions.list'''  % (str(db_addr),str(db_addr),str(session_modes_to_teardown),str(db_machine_password))
        print x
        try:
            os.system(x)
        except:
            traceback.print_exc(file=sys.stdout)         
    f = open('sessions.list', "r")
    lines = f.readlines()
    for line in lines:
        url = "http://%s/mng_session_teardown?id=%s" % (manager, str(line))
#        print url        
        print "send TaerDown for session ID=%s" %(str(line)) 
        #urllib2.urlopen(url,timeout=100)
        mytimeout=float(cfg.teardown_timeout)
        dto = socket.getdefaulttimeout()
        socket.setdefaulttimeout(mytimeout)
        try:
            try:
                f = urllib2.urlopen(str(url))
                x = f.read()
            except socket.error, msg:
                print "timeout"
        except:
            pass
        
        
        finally:
            # restore default
            socket.setdefaulttimeout(dto)       
            
    f.close()
    


def ThrldTeardown(manager):
    global cfg
    manger=cfg.manager
    url = "http://%s/troubleshooting/controlled_playout_teardown_by_url_mode?teardown_dynamic=1&teardown_static=1&teardown_origin=1&teardown_thumbnails=1&teardown_download=1&teardown_repackage_origin=1" % (manager)
    mytimeout=float(cfg.teardown_timeout)
    dto = socket.getdefaulttimeout()
    socket.setdefaulttimeout(mytimeout)
    try:
        try:
            f = urllib2.urlopen(str(url))
            x = f.read()
            print x
        except socket.error, msg:
            print "timeout"
    except:
        pass
# Main ----------------------------------------------------

pars = Parser()
cfg = pars.ini_parse()
#defineLogger()
TearDownPerSec = int(cfg.tear_down_per_sec)
rtsp_managers = cfg.rtsp_managers.split(",")
is_numeic_session_id = int(cfg.is_numeic_session_id)
StreamerID = cfg.streamer_id
isLSCP = int(cfg.playout_mode)
use_db = int(cfg.use_db)
db_addr = str(cfg.db_addr)
db_type = str(cfg.db_type)
db_machine_password = str(cfg.db_machine_password)
teardown_session_mode = str(cfg.teardown_session_mode)
# Getting manager ip from Playout script
manager_ip = Globals.manager_ip()
num_of_session_per_sec_fast_mode = 5
accumulated_list = []
accumulated_list_type_numeric = []
accumulated_list_type_dsmcc = []
accumulated_list_type_string = []
num_of_deletion = 0

#manager = raw_input("What is the Manager IP & port (Press Enter for default manager - %s  ): " % (manager_ip))
manager = manager_ip

# Choosing default Manager ip from Playout script or new given manager ip
if manager == '':
    manager = manager_ip
else:
    manager = manager

# Getting the manager version
Globals.managerObj = Globals.init_manager()

manager_ver = "3.0.0.0"


version_num = pars.stb_ip_parse(manager_ver)

streamers = []

# Setting default timeout to open http connection
socket.setdefaulttimeout(15)
parse_region = None
parse_topology = None
#Getting Region ID to get the streamers list...

if cfg.thrld_teardown == 1:
    ThrldTeardown(manager)
    quit()
else:
    pass



if rtsp_managers[0] == '':
    try:
        try:
            Region_ID_url = "%s%s/get_topology?X=0" % (Globals.managerObj.getHTTP(), manager)
            Region_result = urllib2.urlopen(Region_ID_url)
            xml_Region = Region_result.read()
            parse_region = libxml2.parseDoc(xml_Region)
            if manager_ver == '2.0.0.1':
                Region_ID = checkByxPath(parse_region, "//X/online/elem/base/id")
                #elif (manager_ver == '2.0.0.13') or (manager_ver == '2.0.0.14') or (manager_ver == '2.0.0.15') or (manager_ver == '2.0.0.14') or (manager_ver == '2.0.0.16'):
            elif ((version_num[0] == 2) and (version_num[1] == 0) and (version_num[3] > 12)) or (version_num[1] >= 5) or (
            version_num[1] == 6) or (version_num[1] == 7) or  (version_num[0] == 3):
                Region_ID = checkByxPath(parse_region, "//X/online/regions/elem/id")
            else:
                Region_ID = checkByxPath(parse_region, "//X/online/elem/id")
    
                #print "Region ID = " + str(Region_ID)
    
        except:
            print "Error while trying to get Region ID.\nScript will abort..."
            sys.exit(0)
    
    finally:
        if parse_region:
            parse_region.freeDoc()
    
    
    
    
    #Opening full topology xml to get the streamers list   
    try:
        try:
            topology_url = "%s%s/command/monitor_service?token=&agent=&id=TOPOLOGY&opaque=%s+DATA" % (
                Globals.managerObj.getHTTP(), manager, Region_ID)
            #print "topology url = " + str(topology_url)
            topology_result = urllib2.urlopen(topology_url)
            xml_topology = topology_result.read()
            parse_topology = libxml2.parseDoc(xml_topology)
    
            print parse_topology
            if manager_ver == '9':
                Streamer_ID = StreamerByxPath(parse_topology, "//X/config/edges/elem/streamers/elem/addr")
            else:
                Streamer_ID = StreamerByxPath(parse_topology, "//X/config/edges/elem/streamers/elem/addr")
    
        except Exception,x:
    	    print x
            print "Error while trying to get Streamers list from topology"
            pass
    finally:
        if parse_topology:
            parse_topology.freeDoc()

else:
    for i in range(len(rtsp_managers)):        
        try:
            Region_ID_url = "%s%s/get_topology?X=0" % (Globals.managerObj.getHTTP(), rtsp_managers[i])
            Region_result = urllib2.urlopen(Region_ID_url)
            xml_Region = Region_result.read()
            parse_region = libxml2.parseDoc(xml_Region)
            if manager_ver == '2.0.0.1':
                Region_ID = checkByxPath(parse_region, "//X/online/elem/base/id")
                #elif (manager_ver == '2.0.0.13') or (manager_ver == '2.0.0.14') or (manager_ver == '2.0.0.15') or (manager_ver == '2.0.0.14') or (manager_ver == '2.0.0.16'):
            elif ((version_num[0] == 2) and (version_num[1] == 0) and (version_num[3] > 12)) or (version_num[1] >= 5) or (
            version_num[1] == 6) or (version_num[1] == 7) or  (version_num[0] == 3):
                Region_ID = checkByxPath(parse_region, "//X/online/regions/elem/id")
            else:
                Region_ID = checkByxPath(parse_region, "//X/online/elem/id")
    
                #print "Region ID = " + str(Region_ID)
    
        except:
            print "Error while trying to get Region ID.\nScript will abort..."
            sys.exit(0)
    
        finally:
            if parse_region:
                parse_region.freeDoc()
    
    
    
    
        #Opening full topology xml to get the streamers list   
        try:
            try:
                topology_url = "%s%s/command/monitor_service?token=&agent=&id=TOPOLOGY&opaque=%s+DATA" % (
                    Globals.managerObj.getHTTP(), rtsp_managers[i], Region_ID)
                #print "topology url = " + str(topology_url)
                topology_result = urllib2.urlopen(topology_url)
                xml_topology = topology_result.read()
                parse_topology = libxml2.parseDoc(xml_topology)
        
                print parse_topology
                if manager_ver == '9':
                    Streamer_ID = StreamerByxPath(parse_topology, "//X/config/edges/elem/streamers/elem/addr")
                else:
                    Streamer_ID = StreamerByxPath(parse_topology, "//X/config/edges/elem/streamers/elem/addr")
        
            except Exception,x:
                print x
                print "Error while trying to get Streamers list from topology"
                pass
        finally:
            if parse_topology:
                parse_topology.freeDoc()
    
        
    
    
    
    

# Killing the playout script
try:
    pid_file = open("pid.txt", "r")
    pid_num = pid_file.read()
    Y = os.system('kill -9 %s' % (pid_num))
    Z = os.system('rm -f pid.txt')
except:
    "Error while trying to kill the playout script"
    pass


# Counting number of streamers
num_streamers = len(streamers)  #for the use in the loop afterwards
threads = []
if use_db == 0 :
    #********** Running in Serialized Mode *********
    if(TearDownPerSec != 0):
        print "*** Running in Serialized Mode ***"
        #    rtsp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #    onlyManager = manager[:string.find(manager,":")]
        #print onlyManager
        #    rtsp_sock.connect((str(onlyManager).strip(),554))
    
        for i in range(num_streamers):
            analyzing_streamers = streamers_sessions(streamers[i])
        Session_Deletion(TearDownPerSec)
    #    rtsp_sock.close()
    #*********   Running in fast Multi Threaded Mode **************
    else:
        print "*** Running in fast Multi Threaded Mode ***"
        lock = threading.RLock()
        for i in range(num_streamers):
            t = MyThread(streamers_sessions, (streamers[i],), streamers_sessions.__name__)
            threads.append(t)
    
        for i in range(num_streamers):
            threads[i].start()
    
        for i in range(num_streamers):
            threads[i].join()
    
        print 'all DONE'
    print "\n<<************* TOTAL num of deletion: %d ***************>>>" % (num_of_deletion)
    # Deleting all temporary "wget" sessions...
    rem_mng_files = os.system('find . -name  "mng_session*" -delete ')
else:
    del_from_db()

