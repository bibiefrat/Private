#!/usr/bin/python
import math
import datetime
from datetime import date
import sys
import os
import string
import time
import urllib2
import urllib
import libxml2
import logging
from configobj import ConfigObj
import signal
import socket
from datetime import timedelta
import random
import xml.sax.saxutils
from bisect import bisect
import requests

class globalParams:
    def __init__(self):
        self.success_ingests = 0
        self.failed_ingests = 0
        self.ingest_concurrent_counter = 1
        self.manager = ""
        self.streamer = ""
        self.streamer_no_port = ""
        self.url_num_ingests = ""
        self.total_ingests = ""
        self.concurrent_ingests = ""
        self.multicast_addr = ""
        self.start_time = ""
        self.end_time = ""
        self.is_delay = ""
        self.sec_delay = ""
        self.director = urllib.quote_plus("director abc")
        self.actor = urllib.quote_plus("actor abc")
        self.year = urllib.quote_plus(str(2000))
        self.is_proxy = 0
        self.managers = []
        self.regions = []
        
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def signal_handler(signal, frame):
    raise SystemExit

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def defineLogger():
    # Defining the log level and handling
    
    print "Log level = %s" % (log_level)
    
    
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
    
    formatter = logging.Formatter("[%(asctime)-19s] %(name)-8s: [%(levelname)-8s] %(message)26s", datefmt='%d-%m-%Y %H:%M:%S')
    
    logging.basicConfig(level=log_print,
                        format="[%(asctime)-19s] %(name)-8s: [%(levelname)-8s] %(message)26s",
                        datefmt='%d-%m-%Y %H:%M:%S',
                        filename=path+"/"+params.log_file,
                        filemode='w')
    
    console = logging.StreamHandler()
    console.setLevel(log_print)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    signal.signal(signal.SIGINT, signal_handler)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def pars_INI_file(configFile):
    global params
    global Region_ID
    global Edge_ID
    
    params.manager = str(configFile['Configuration']['manager']).strip()
    params.streamer = str(configFile['Configuration']['streamer']).strip()
    params.start_time = int(str(configFile['Configuration']['start_time']).strip())
    params.end_time = int(str(configFile['Configuration']['end_time']).strip())
    params.total_ingests = int(str(configFile['Configuration']['total_ingests']).strip())
    params.concurrent_ingests = int(str(configFile['Configuration']['concurrent_ingests']).strip())
    params.sec_delay = float(str(configFile['Configuration']['num_sec_delay']).strip())
    params.log_file =  str(configFile['Configuration']['log_file_location']).strip()
    params.streamer_no_port = params.streamer[:string.find(params.streamer, ":")]
    params.no_delay_sessions = int(str(configFile['Configuration']['no_delay_sessions']).strip())
    params.num_home_id = int(str(configFile['Configuration']['num_home_id']).strip())
    params.num_stb_per_home = int(str(configFile['Configuration']['num_stb_per_home']).strip())
    params.basic_home_id = int(str(configFile['Configuration']['basic_home_id']).strip())
    params.basic_mac = int(str(configFile['Configuration']['basic_mac']).strip())
    params.home_id_service_group = str(configFile['Configuration']['home_id_service_group']).strip()
    params.box_size = int(str(configFile['Configuration']['box_size']).strip())
    params.add_recording_to_exist_env = int(str(configFile['Configuration']['add_recording_to_exist_env']).strip())
    params.channel_list_file = str(configFile['Configuration']['channel_list_file']).strip()
    params.use_current_channels = str(configFile['Configuration']['use_current_channels']).strip()
    params.rand_time = int(str(configFile['Configuration']['rand_time']).strip())
    params.is_rsdvr_rev3 = int(str(configFile['Configuration']['is_rsdvr_rev3']).strip())
    params.box_dist_by_sg = str(configFile['Configuration']['box_dist_by_sg']).strip()
    params.random_shuffle_boxes = int(str(configFile['Configuration']['random_shuffle_boxes']).strip())
    params.no_delay_boxes = int(str(configFile['Configuration']['no_delay_boxes']).strip())
    params.num_sec_delay_prov = int(str(configFile['Configuration']['num_sec_delay_prov']).strip())
    params.open_sock_once = int(str(configFile['Configuration']['open_sock_once']).strip())
    params.ena_rec_per_sec = int(str(configFile['Configuration']['ena_rec_per_sec']).strip())
    params.rec_per_sec = int(str(configFile['Configuration']['rec_per_sec']).strip())
    params.riab_mode = int(str(configFile['Configuration']['riab_mode']).strip())
    params.one_starting_time = int(str(configFile['Configuration']['one_starting_time']).strip())
    params.srm_id = int(str(configFile['Configuration']['srm_id']).strip())
    params.home_profile = str(configFile['Configuration']['home_profile']).strip()
    params.home_profile_dist_per_sg = str(configFile['Configuration']['home_profile_dist_per_sg']).strip()
    params.use_home_profile = int(str(configFile['Configuration']['use_home_profile']).strip())
    params.QuotaType = int(str(configFile['Configuration']['QuotaType']).strip())
    params.Type = int(str(configFile['Configuration']['Type']).strip())
    
    
    
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 
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
            elif freq >1e-8:
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
        return lambda rnd=random.random, bis=bisect: objects[bis(addedFreq, rnd()*lastSum)]
    else:
        return lambda rnd=random.random, bis=bisect: objects[bis(addedFreq, rnd())]




    
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 

def print_open_details():
    global params
    if params.streamer == '' :
        log.info("=" * 60 + "\n" + " " * 46 + "Configuration details :\n" + " " * 43 + "   Manager is  : %s .\n" % (params.manager) + " " * 43 + "   Total Number of ingests to reach : %s .\n" % str(params.total_ingests) + " " * 43 + "   Recordings per bulk : %s .\n" % str(params.no_delay_sessions) + " " * 43 + "   Number of concurrent ingests : %s .\n" % str(params.concurrent_ingests) + " " * 43 + "=" * 60 )
    else :
        log.info("=" * 60 + "\n" + " " * 46 + "Configuration details :\n" + " " * 43 + "   Manager is  : %s .\n" % (params.manager) + " " * 43 + "   Streamer is : %s .\n" % (params.streamer) + " " * 43 + "   Total Number of ingests to reach : %s .\n" % str(params.total_ingests) + " " * 43 + "   Recordings per bulk : %s .\n" % str(params.no_delay_sessions) + " " * 43 + "   Number of concurrent ingests : %s .\n" % str(params.concurrent_ingests) + " " * 43 + "=" * 60 )    

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def print_end_details():
    global params
    
    log.info("=!" * 30 + "\n" + " " * 43 + "Total successful ingests allocation to the system =  %d\n" % (params.success_ingests) + " " * 43 + "Total failed ingests allocation to the system =  %d\n" % (params.failed_ingests) + " " * 43 + "end of script\n" + " " * 43 + "=!" * 30)
    

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Editing the XML for the Streamer load
def addByxPath(dom, xpath):               
    list = dom.xpathEval(xpath)
    for url in list:
        o = url.content
        #print "o in function-->" +params.manager o
    return o

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Editing the XML to find the error in case ingest fails
def checkByxPath(dom, xpath):               
    list = dom.xpathEval(xpath)
    for url in list:
        r = int(url.content)
    
    return r    
 
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Finding the concurrent ingest number on the system
def checkStrByxPath(ingest_counter, dom, xpath):  
   
    list = dom.xpathEval(xpath)
    for url in list:
        r = int(url.content)
        #print "r -->\n" + str(r)
        #if int(r) == 1:
        #    ingest_counter += 1
    #print "r in func-->" + str(r)        
    return r  

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def get_streamer_load(streamer):
    
    str_load = "http://" + streamer + "/cvmx_work_load?X=0"
    dom = None
    try:
        try:
            str_response = urllib2.urlopen(str_load)
            xml = str_response.read()
            dom = libxml2.parseDoc(xml)
            result = addByxPath(dom, "//X/total_load")
            log.info ("Streamer current load : %s %%" % (result))
        except urllib2.URLError, err:
            log.critical ("Couldn't get streamer load : %s " % (err.reason))
    finally:
        if dom:
              dom.freeDoc()
    

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def check_existing_ingests(url_num_Of_ingests, Ingest_Counter):
    global params
    parse_Ingests_Num = None    
    if params.is_proxy == 0:
        if params.riab_mode == 0:
            try:
                try:
                    #print "check existing ingests -->" + str(params.url_num_ingests)
                    Ingests_Num_result = urllib2.urlopen(params.url_num_ingests)        
                    xml_Ingests_Num = Ingests_Num_result.read()
                    parse_Ingests_Num = libxml2.parseDoc(xml_Ingests_Num)
                    
                    if params.streamer == '': 
                        Ingests_Num = int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[9]"))
                        Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[17]"))
                        Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[18]"))
                        Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[19]"))
                        Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[20]"))
                        #Ingests_Num = int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "//X/summary/elem/ingest_sessions"))
                    else:
                        Ingests_Num = int(checkByxPath(parse_Ingests_Num, "//X/size"))
                    log.info("=" * 60 + "\n" + " " * 43 + "Existing Concurrent ingests = %d\n" % (Ingests_Num) + " " * 43 + "=" * 60 ) 
            
                    
                except:
                    Ingests_Num = params.concurrent_ingests
                    log.error("=" * 60 + "\n" + " " * 43 + "Can not retrieve the number of concurrent ingests.\n" + " " *43 + "Manager did not respond .\n" + " " *43 + "Assuming Concurrent ingests = %d\n" % (Ingests_Num) + " " *43 + "=" * 60  ) 
                    pass
            finally:
                if parse_Ingests_Num:
                    parse_Ingests_Num.freeDoc()
            
          #  log.info("=" * 60) + "\n" + " " *43 )
              #  log.info("Can not retrieve the number of concurrent ingests.\n" + " " *43 + "Manager did not respond .")
              #  log.info("Existing Concurrent ingests = %s" % (Ingests_Num))
              #  log.info("=" * 60)
        
            return Ingests_Num
        else:
            Ingests_Num = 0
            return Ingests_Num
    #IF this is manager proxy
    else:
        Ingests_Num = 0
        if params.riab_mode == 0:       
            for i in range(len(params.managers)):                 
                params.url_num_ingests = "http://%s/get_session_state?id=0&reg_id=%s&edge_id=0&first=0&last=0 " % (params.managers[i], params.regions[i])
                try:
                    try:
                        #print "check existing ingests -->" + str(params.url_num_ingests)
                        Ingests_Num_result = urllib2.urlopen(params.url_num_ingests)        
                        xml_Ingests_Num = Ingests_Num_result.read()
                        parse_Ingests_Num = libxml2.parseDoc(xml_Ingests_Num)
                        
                        if params.streamer == '':
                            per_manager_ingest = Ingests_Num                     
                            Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[9]"))                         
                            Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[17]"))
                            Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[18]"))
                            Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[19]"))
                            Ingests_Num += int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "/X/num_in_state/elem[20]"))
                            per_manager_ingest = Ingests_Num - per_manager_ingest
                            #Ingests_Num = int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "//X/summary/elem/ingest_sessions"))
                        else:
                            Ingests_Num = int(checkByxPath(parse_Ingests_Num, "//X/size"))
                        log.info("=" * 60 + "\n" + " " * 43 + "Existing Concurrent ingests on manager %s = %d\n" % (params.managers[i],per_manager_ingest) + " " * 43 + "=" * 60 ) 
                
                        
                    except:
#                        Ingests_Num = params.concurrent_ingests
                        log.error("=" * 60 + "\n" + " " * 43 + "Can not retrieve the number of concurrent ingests in manager %s.\n" % (params.managers[i])  + " " *43 + "Manager did not respond .\n" + " " *43 + "Assuming Concurrent ingests = %d\n" % (Ingests_Num) + " " *43 + "=" * 60  ) 
                        pass
                finally:
                    if parse_Ingests_Num:
                        parse_Ingests_Num.freeDoc()
                        parse_Ingests_Num=None
            log.info("=" * 60 + "\n" + " " * 43 + "Existing Concurrent total ingests = %d\n" % (Ingests_Num) + " " * 43 + "=" * 60 )
            return Ingests_Num    
        else:
           Ingests_Num = 0
           return Ingests_Num     
            
            
            
            
            
            
            
        
            #CM_ver = addByxPath(manager_parse_ver, "//X/cm_ver")
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def stb_ip_parse(ip):
    
        ipNums = ip.split('.')
        ipNums[0] = int(ipNums[0]) 
        ipNums[1] = int(ipNums[1])
        ipNums[2] = int(ipNums[2])
        ipNums[3] = int(ipNums[3])
        
        return ipNums

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def str_stb_ip_parse(ip):
    
        ip[0] = str(ip[0]) 
        ip[1] = str(ip[1])
        ip[2] = str(ip[2])
        ip[3] = str(ip[3])   
       
        new_ip = '.'.join(ip)
        
        return new_ip

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def remote_date(manager_ip):
    manager_ip = manager_ip[:string.rfind(manager_ip,":")]
    print "manager ip in ssh-->"+ manager_ip
    ssh_newkey = 'Are you sure you want to continue connecting'
    # my ssh command line
    p=pexpect.spawn('ssh vsadmin@%s date +%%s'% (manager_ip)) 

    i=p.expect([ssh_newkey,'password:',pexpect.EOF])
    if i==0:
        print "I say yes"
        p.sendline('yes')
        i=p.expect([ssh_newkey,'password:',pexpect.EOF])
    if i==1:
        print "I give password",
        p.sendline("vsadmin")
        p.expect(pexpect.EOF)
    elif i==2:
        print "I either got key or connection timeout"
        pass
    #print p.before # print out the result

    return p.before


##
# This is a simple function.  This is the description.
# @param recording_chunk_list this is the chuck size
# @param batch_size this is the batch size
# @author: bibi
##

def RSDVRRecording(recording_chunk_list,batch_size, rsdvr_rev):
    global params
    global id
    if params.is_rsdvr_rev3 !=2 and params.is_rsdvr_rev3 !=3:  
        if params.srm_id == 0:
            id = int(time.time()*1000)
            #id='erez23'
            msg = '<?xml version="1.0" encoding="utf-8"?><ScheduleRecording AssetID = "%s%s%s" CallSign = "%s" StartTime = "%s" EndTime = "%s" > <PVRList>' % (str(recording_chunk_list[0][1]),str(recording_chunk_list[0][0]),xml.sax.saxutils.escape(str(id)) ,recording_chunk_list[0][1] ,recording_chunk_list[0][2] ,recording_chunk_list[0][3])
            #msg = '<?xml version="1.0" encoding="utf-8"?><ScheduleRecording AssetID = "%s" CallSign = "%s" StartTime = "%s" EndTime = "%s" > <PVRList>' % (xml.sax.saxutils.escape(str(id)) ,recording_chunk_list[0][1] ,recording_chunk_list[0][2] ,recording_chunk_list[0][3])
        ###### create XML message########
        else:
            id = id +1
            #msg = '<?xml version="1.0" encoding="utf-8"?><ScheduleRecording AssetID = "%s%s" CallSign = "%s" StartTime = "%s" EndTime = "%s" > <PVRList>' % (str(recording_chunk_list[0][1]),xml.sax.saxutils.escape(str(id)) ,recording_chunk_list[0][1] ,recording_chunk_list[0][2] ,recording_chunk_list[0][3])  
            msg = '<?xml version="1.0" encoding="utf-8"?><ScheduleRecording AssetID = "%s" CallSign = "%s" StartTime = "%s" EndTime = "%s" > <PVRList>' % (xml.sax.saxutils.escape(str(id)) ,recording_chunk_list[0][1] ,recording_chunk_list[0][2] ,recording_chunk_list[0][3])
        #
        
           
        for i in range(batch_size):
            msg += '<PVRListItem  HomeID="%s" MACAddress="%s" />' % (str(recording_chunk_list[i][4]),str(recording_chunk_list[i][5]))        
              
            
        msg += '</PVRList></ScheduleRecording>'
        
        print "send xml:\n" + msg
        print_errors=int(1)
        
        manager_ip = params.manager[:string.find(params.manager,":")]
        manager_port = int(params.manager[string.find(params.manager,":") + 1:])
        length=len(msg)  
        #print "length --> ", length
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        initial_time = time.time()
        s.connect((manager_ip,manager_port )) 
        time_after_connect = time.time()
        connect_time = time_after_connect - initial_time
        print "Connect time : %s\n" % (connect_time)
        s.send("POST /%s HTTP/1.0\r\n" % (rsdvr_rev))
    #    print "POST /%s HTTP/1.0\r\n" % (rsdvr_rev)
        s.send("Content-Type: text/xml\r\n")
        s.send("Content-Length: "+str(length)+"\r\n\r\n")
    
        try : 
            s.sendall(msg)
            time_after_send_msg = time.time()
            msg_send_time = time_after_send_msg - initial_time
            if msg_send_time > print_errors :
              print "Time Out - Sending msg time : %s > %s\n" % (str(msg_send_time),str(print_errors))
            else:
              print "Sending msg time : %s\n" % (msg_send_time)
              
            datarecv=s.recv(512)
            print "Reply Received: "+ str(datarecv)
            if (str(datarecv).find("HTTP/1.0 200 OK") != -1):
                params.success_ingests += batch_size
            else:
                params.failed_ingests += batch_size
        
        except socket.error,message :
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n MSG was not sent due to the following socket error : %s \n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n " % (str(message))
        
        s.close()
        time_after_closing_socket = time.time()
        close_socket_time = time_after_closing_socket - initial_time
        print "Closing socket time : %s\n" % (close_socket_time)
        
        return
    else: # V2 provision API - time based
        if params.srm_id == 0:
            id = int(time.time()*1000)
        else:
            id = id +1
            
        xml_msg = '''<ScheduleRecordings>
<ShowingID>%s_%s</ShowingID>
<Channel>%s</Channel>
<StartTime>%s</StartTime>
<EndTime>%s</EndTime>
<Homes>
 ''' % (str(recording_chunk_list[0][1]),xml.sax.saxutils.escape(str(id)),str(recording_chunk_list[0][1]),str(recording_chunk_list[0][2]),str(recording_chunk_list[0][3]))
        xml_msg2=''
        for i in range(batch_size):
            if params.is_rsdvr_rev3 == 3:
                box_id = 'NPVR'
            elif params.is_rsdvr_rev3 == 2:
                box_id = str(recording_chunk_list[i][4])
            xml_msg2 = xml_msg2 + '''<Home HomeID="%s">
 <RecordingMetadata>
  <Data Name="Title" Value="Michaels show"/>
  <Data Name="Creator" Value="RecomendationPortal"/>
 </RecordingMetadata>
</Home>
''' % (str(box_id))
        
        xml_msg3 = '''</Homes>
</ScheduleRecordings>'''
        xml_msg = xml_msg + xml_msg2 + xml_msg3
        print xml_msg
        headers = {'Content-Type' : 'text/x-xml2'}
        try:
            requests.post('http://' + str(params.manager) + '/v2/recordings/', data=xml_msg, headers=headers, verify=False, timeout=20)
        except : #this confirms you that the request has reached server
            pass


def RSDVRRecordingSockOnce(recording_chunk_list,batch_size, rsdvr_rev):
    global params
    global sock
    id = int(time.time()*1000)
    
    ###### create XML message########
       
    msg = '<?xml version="1.0" encoding="utf-8"?><ScheduleRecording AssetID = "%s%s%s" CallSign = "%s" StartTime = "%s" EndTime = "%s" > <PVRList>' % (str(recording_chunk_list[0][1]),str(recording_chunk_list[0][0]),xml.sax.saxutils.escape(str(id)) ,recording_chunk_list[0][1] ,recording_chunk_list[0][2] ,recording_chunk_list[0][3])
#    msg = '<?xml version="1.0" encoding="utf-8"?><ScheduleRecording AssetID = "11100001" CallSign = "%s" StartTime = "%s" EndTime = "%s" > <PVRList>' % (recording_chunk_list[0][1] ,recording_chunk_list[0][2] ,recording_chunk_list[0][3])
       
    for i in range(batch_size):
        msg += '<PVRListItem  HomeID="%s" MACAddress="%s" />' % (str(recording_chunk_list[i][4]),str(recording_chunk_list[i][5]))        
          
        
    msg += '</PVRList></ScheduleRecording>'
    
    #print "send xml:\n" + msg
    print_errors=int(1)
    
    #manager_ip = params.manager[:string.find(params.manager,":")]
    #manager_port = int(params.manager[string.find(params.manager,":") + 1:])
    length=len(msg)  
    #print "length --> ", length
    
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #initial_time = time.time()
    #s.connect((manager_ip,manager_port )) 
    #time_after_connect = time.time()
    #connect_time = time_after_connect - initial_time
    #print "Connect time : %s\n" % (connect_time)
    try :
        send_start = time.time()
        #sock.send("POST /%s HTTP/1.0\r\n" % (rsdvr_rev))
        #sock.send("Connection: keep-alive\r\n")
    #    print "POST /%s HTTP/1.0\r\n" % (rsdvr_rev)
        #sock.send("Content-Type: text/xml\r\n")
        #sock.send("Content-Length: "+str(length)+"\r\n\r\n")
        
        
        header = '''POST /%s HTTP/1.0
Connection: keep-alive
Content-Type: text/xml
Content-Length: %s

''' % ((rsdvr_rev), str(length))
        #sock.send(header)
        msg_total = header + msg
        #print "POST /%s HTTP/1.0\r\n" % (rsdvr_rev)
        #print "Connection: keep-alive\r\n"
        #print "Content-Type: text/xml\r\n"
        #print "Content-Length: "+str(length)+"\r\n\r\n"
     
        #sock.sendall(msg_total)
        sock.send(msg_total)
        send_end = time.time()
        if (send_end - send_start) > 0.02 :
            print "took more than 0.02 sec"
        #time_after_send_msg = time.time()
        #msg_send_time = time_after_send_msg - initial_time
#        if msg_send_time > print_errors :
#          print "Time Out - Sending msg time : %s > %s\n" % (str(msg_send_time),str(print_errors))
#        else:
#          print "Sending msg time : %s\n" % (msg_send_time)
#        recv_start = time.time() 
        datarecv=sock.recv(640)
        #print datarecv
#        recv_end = time.time()
#        print "send time = %s    recv time = %s" % (str(send_end - send_start),  str(recv_end - recv_end))
     #   print "Reply Received: %s\r\n ^^^^" % str(datarecv)
        #if (str(datarecv).find("HTTP/1.0 200 OK") != -1):
        #    params.success_ingests += batch_size
        #else:
        #    params.failed_ingests += batch_size
    
    except socket.error,message :
        print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n MSG was not sent due to the following socket error : %s \n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n " % (str(message))
    
    #s.close()
    #time_after_closing_socket = time.time()
    #close_socket_time = time_after_closing_socket - initial_time
    #print "Closing socket time : %s\n" % (close_socket_time)
    
    return
   





   
def CreateHomeIDs(box_size, rsdvr_rev):
    # initializing the url responses for the exceptions
    global params
    home_id = params.basic_home_id
    for i in range(params.num_home_id):
        url = "http://%s/%s?type=ProvisionHome&HomeID=%s&AllocationSize=%s&ServiceGroup=%s&size=0" % (params.manager, rsdvr_rev, str(home_id), str(box_size), str(params.home_id_service_group))
        #print "*********" , url
        url_result = urllib2.urlopen(url)
        print url
        #xml_Home_ID = url_result.read()
        #parse_Home_ID = libxml2.parseDoc(xml_Home_ID)
        home_id += 1
    return

def create_home_profile_array(boxes_by_sg):
    home_profile_array = []
    num_sg_array = []  
    home_profile_array_all_sg = []   
    service_group_array = params.home_id_service_group.split(';')
    home_profile_array = params.home_profile.split(';')
    
    objs = ""
    home_profile_dist_per_sg_array = map(int, params.home_profile_dist_per_sg.split(';'))
    
    
    for j in range(len(service_group_array)):
        counter=0
        for i in range(len(boxes_by_sg)):
            if service_group_array[j] == boxes_by_sg[i]:
                counter += 1
        num_sg_array.append(counter) 
    print num_sg_array
    for j in range(len(service_group_array)): 
        wc = wchoice(home_profile_array, home_profile_dist_per_sg_array, filter=False)    
        home_profile_array_per_sg = [wc() for _ in xrange(num_sg_array[j])]
        home_profile_array_all_sg.append(home_profile_array_per_sg)
    
    return home_profile_array_all_sg
#    for j in range(len(service_group_array)):
#        print service_group_array[j]                   
#        print home_profile_array_all_sg [j]
    
    
    
    
    
    
    
def CreateHomeIDs1(box_size, rsdvr_rev):
    # initializing the url responses for the exceptions
    global params
    home_id = params.basic_home_id
    service_group_array = params.home_id_service_group.split(';')
    objs = "RS"
    sg_percentage_array = map(int, params.box_dist_by_sg.split(';'))   
    home_profile_per_sg_counter = [0] * len(service_group_array)
    
    #freqs = [int(cfg.ff_percent),int(cfg.rew_percent),int(cfg.pause_percent)]        
    wc = wchoice(service_group_array, sg_percentage_array, filter=False)
    
    boxes_by_sg = [wc() for _ in xrange(params.num_home_id)]
    home_profile_array = create_home_profile_array(boxes_by_sg)
    if(params.random_shuffle_boxes == 1):
        random.shuffle(boxes_by_sg)
    else:
        boxes_by_sg =  sorted(boxes_by_sg)
    count = 0
    bulk_counter = 1
    for i in range(params.num_home_id):
        if params.use_home_profile == 0:
            if params.is_rsdvr_rev3 == 1:
                url = "http://%s/%s?type=ProvisionHome&HomeID=%s&AllocationSize=%s&ServiceGroup=%s&size=0" % (params.manager, rsdvr_rev, str(home_id), str(box_size), str(boxes_by_sg[count]))
            # V2 provision API - time based
            elif params.is_rsdvr_rev3 == 2:
                xml = """<ProvisionHome HomeID="%s" GeoID="%s" Quota="%s" QuotaType="%s" Type="%s" />""" % (str(home_id),str(boxes_by_sg[count]), str(box_size),str(params.QuotaType),str(params.Type))
                headers = {'Content-Type' : 'text/x-xml2'}
                requests.post('http://' + str(params.manager) + '/v2/homes/', data=xml, headers=headers)
        else:
            for i in range(len(service_group_array)):
                if service_group_array[i] == boxes_by_sg[count] :
                    url = "http://%s/%s?type=ProvisionHome&HomeID=%s&AllocationSize=%s&ServiceGroup=%s&HomeProfile=%s&size=0" % (params.manager, rsdvr_rev, str(home_id), str(box_size), str(boxes_by_sg[count]),str(home_profile_array[i][home_profile_per_sg_counter[i]]))
                    home_profile_per_sg_counter[i] += 1
                else:
                    pass
        #print "*********" , url
        if params.is_rsdvr_rev3 != 2:
            url_result = urllib2.urlopen(url)
            print url
        #xml_Home_ID = url_result.read()
        #parse_Home_ID = libxml2.parseDoc(xml_Home_ID)
        home_id += 1
        count += 1
        if bulk_counter == params.no_delay_boxes:
            bulk_counter = 1
            time.sleep(params.num_sec_delay_prov)
        else:
           bulk_counter += 1 
    return



def CretaeSTBs(rsdvr_rev):
    global params
    stb_mac = params.basic_mac
    home_id = params.basic_home_id
    for i in range(params.num_home_id):
        for j in range(params.num_stb_per_home):
            if rsdvr_rev == 'v2':
                return
#                url = "http://%s/%s?type=AddSTB&HomeID=%s&MACAddress=%s&AllocationSize=0" % (params.manager, rsdvr_rev,str(home_id),str(stb_mac))
            else:
                url = "http://%s/Rev3_RSDVR?type=AddSTB&HomeID=%s&MACAddress=%s&AllocationSize=0" % (params.manager, str(home_id),str(stb_mac))
            #print "*********" , url
            url_result = urllib2.urlopen(url)
            print url
            #xml_STB = url_result.read()
            #parse_STB = libxml2.parseDoc(xml_STB)
            stb_mac += 1
        home_id += 1    


def GetChannelMapFromFile(file, path):
    try:
            channels_file = open(path+"/" + file, "r")
            
    except IOError:
            print "Channels file can not be found.\nScript finished."
            sys.exit(0)
    
    all_lines = channels_file.readlines()
    num_channels_lines = len(all_lines) 
    channel_list = []
    for single_lines in all_lines:
        channel_list.append(str(single_lines).strip())
    return channel_list
        
     

def GetChannelMapFromEnvironment(version_num):
    global params
    channel_list = []
    if (params.is_rsdvr_rev3 == 0 or params.is_rsdvr_rev3 == 2 or params.is_rsdvr_rev3 == 3):
        if (version_num[0] == 2) and (version_num[1] == 6) and (version_num[3] >= 4) or (version_num[1] >= 7) or (version_num[0] >= 3) :
            channels_url = "http://%s/multicast_channel/get_all?offset=0&limit=10000" % (str(params.manager))
        else :
            channels_url = "http://%s/multicast_channel/get_all?X=0" % (str(params.manager))
        #print "channels url -->", channels_url
        channel_url_result = urllib2.urlopen(channels_url)
        xml_channel_url = channel_url_result.read()
        parse_channels = libxml2.parseDoc(xml_channel_url)
        if (version_num[0] == 2) and (version_num[1] == 6) and (version_num[3] >= 4) or (version_num[1] >= 7) or  (version_num[0] >= 3) : 
            list = parse_channels.xpathEval("//X/value/channels/elem/name")
        else :
            list = parse_channels.xpathEval("//X/value/elem/name")
            
        for url in list:
            channel_list.append(url.content)
        parse_channels.freeDoc()  
        return channel_list
    else:
        channels_url = "http://%s/Rev3_RSDVR?type=GetChannelMapData" % (str(params.manager))
        channel_url_result = urllib2.urlopen(channels_url)
        xml_channel_url = channel_url_result.read()
        parse_channels = libxml2.parseDoc(xml_channel_url)
        #print xml_channel_url
        #list = parse_channels.xpathEval("//ChannelList/ChannelData")
        if (version_num[0] >= 2):
            list = parse_channels.xpathEval("/*/*")
            for url in list:            
                channel_list.append(url.prop("ChannelName"))
        else:
            list = parse_channels.xpathEval("//X/obj/ChannelData/elem/ChannelName")
            for url in list:            
                channel_list.append(url.content)
        parse_channels.freeDoc()  
        return channel_list

def get_manager_version(manager):
    manager_parse_ver = None
    try:
        try :
            manager_ver_url = "http://%s/get_versions?X=0" % (manager)
            #print manager_ver_url
            manager_ver_open_url=urllib2.urlopen(manager_ver_url)
            manager_ver_response = manager_ver_open_url.read()
            manager_parse_ver = libxml2.parseDoc(manager_ver_response)
            manager_ver = addByxPath(manager_parse_ver, "//X/mngr_ver")
            #CM_ver = addByxPath(manager_parse_ver, "//X/cm_ver")
            #print "manager version --> " + str(manager_ver)
            
        except :
            log.critical("=!" * 30 + "\n" + " " * 43 + "Manager didn't respond ...\n" + " " * 43 + "Script exit\n" + " " * 43 + "=!" * 30 )  
            sys.exit()
    finally:
        if manager_parse_ver:
            manager_parse_ver.freeDoc()
        
    return manager_ver

def check_if_manager_proxy():
    url = "http://%s/fxhelp" % (params.manager)
    manager_fxhelp_open_url=urllib2.urlopen(url)
    manager_fxhelp_response = manager_fxhelp_open_url.read()
    #manager_parse_fxhelp = libxml2.parseDoc(manager_fxhelp_response)
    if (str(manager_fxhelp_response).find("Manager Proxy") != -1):
        params.is_proxy = 1
        url = "http://%s/get_regions?X=0" % str(params.manager)
        regions_open_url=urllib2.urlopen(url)
        regions_response = regions_open_url.read()
        regions_parse = libxml2.parseDoc(regions_response)
        list = regions_parse.xpathEval("//X/regs/elem/id")
        #list = xpathEval(regions_parse, "//X/regs/elem/id")
        for url in list:
            params.regions.append(url.content)
        list = regions_parse.xpathEval("//X/regs/elem/manager_addr")
        for url in list:
            params.managers.append(url.content)
    else:
        params.is_proxy = 0
         

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def main():
    global id
    #Setting default timeout
    socket.setdefaulttimeout(60)
    
    global params
    global channels_list
    
    # Getting the Manager version
    manager_version = get_manager_version(params.manager)
    print "Manager version = %s\n" % (manager_version)
   
    version_num = stb_ip_parse(manager_version)
            
    Ingest_Counter = 0 
    parse_region = None
    parse_edge = None
    print_open_details()
    
    check_if_manager_proxy()
#    if params.is_rsdvr_rev3==2:
#        params.no_delay_sessions = 1
    
    if params.is_proxy == 0:
        #Checking Region ID to receive concurrent ingests
        try:
            try:
                    Region_ID_url = "http://%s/get_topology?X=0" % (params.manager)
                    Region_result = urllib2.urlopen(Region_ID_url)
                    xml_Region = Region_result.read()
                    parse_region = libxml2.parseDoc(xml_Region)
                    if manager_version == '2.0.0.1':
                        Region_ID = checkByxPath(parse_region, "//X/online/elem/base/id")
                    elif ((version_num[0] == 2) and (version_num[1] == 0) and (version_num[3] > 12)) or (version_num[1] == 5) or (version_num[1] == 6) or (version_num[1] >= 7) or (version_num[0] >= 3): 
                        Region_ID = checkByxPath(parse_region, "//X/online/regions/elem/id")
                    else:
                        Region_ID = checkByxPath(parse_region, "//X/online/elem/id")
                                    
                    #print "Region ID = " + str(Region_ID)
                
            except:
                    print "Error while trying to get Region ID"
                    print "url --> " + str(Region_ID_url)
                    pass
        finally:
            if parse_region:
                parse_region.freeDoc()
        
        #Checking Edge ID to receive concurrent ingests
        try:
            try:
                    Edge_ID_url = "http://%s/command/monitor_service?token=&agent=&id=TOPOLOGY&opaque=%s+DATA" % (params.manager, Region_ID)
                    Edge_result = urllib2.urlopen(Edge_ID_url)
                    xml_edge = Edge_result.read()
                    parse_edge = libxml2.parseDoc(xml_edge)
                    if manager_version == '2.0.0.1':
                        Edge_ID = checkByxPath(parse_edge, "//X/config/base/id")
                    else:
                        Edge_ID = checkByxPath(parse_edge, "//X/config/id")
                                   
                    #print "Edge ID = " + str(Edge_ID)
                
            except:
                    print "Error while trying to get Edge ID"
                    print "url --> " + str(Edge_ID_url)
                    pass
        finally:
            if parse_edge:
                  parse_edge.freeDoc() 
    if  (params.is_proxy == 1 and params.is_rsdvr_rev3 == 2) or (params.is_proxy == 1 and params.is_rsdvr_rev3 == 3):
        print "This is Proxy with Provision V2 - so all schedule recording are directly via managers"
        return    
    line_index = 0
    Real_index = 0
    channel_counter = 0 
    channel_len = int (len(channels_list))
    channel_prefix = "Channel_"
    home_id = params.basic_home_id
    stb_mac = params.basic_mac
    home_id_counter = 0
    mac_counter = 0
    recording_chunk_list = []
    single_rec_list = []
    chunk_counter = 0
    batch_size = 0
    orig_batch_size = 0
    end_time = params.end_time
    if (params.ena_rec_per_sec == 1):
        params.no_delay_sessions = 1
    
        
# you can't send the same HOME ID in a single batch- since asset ID is derivative of the home id - you cant have duplicates
# also check the case where total recording is less than batch size   
    if (params.num_home_id < params.no_delay_sessions):        
        if params.num_home_id < params.total_ingests :
            print "<<<<<<<< *** Batch Size was altered since number of Boxes is smaller than no Delay Sessions and is set to: %s *** >>>>>>>>\n" % (params.num_home_id)
            if params.num_home_id < params.concurrent_ingests:
                batch_size = params.num_home_id 
            else:
                 batch_size =  params.concurrent_ingests        
        else:
            print "<<<<<<<< *** Batch Size was altered since number batch size is smaller than no Total Sessions and is set to: %s *** >>>>>>>>\n" % (params.total_ingests)
            if params.total_ingests < params.concurrent_ingests:
                batch_size = params.total_ingests
            else:
                batch_size =  params.concurrent_ingests
    else:
        if params.no_delay_sessions <= params.total_ingests:
            if params.no_delay_sessions < params.concurrent_ingests:
                batch_size = params.no_delay_sessions
            else:
                batch_size = params.concurrent_ingests
        else:
            print "<<<<<<<< *** Batch Size was altered since number batch size is smaller than no Total Sessions and is set to: %s *** >>>>>>>>\n" % (params.total_ingests)
            if params.no_delay_sessions < params.concurrent_ingests:
                batch_size =  params.total_ingests
            else:
                batch_size = params.concurrent_ingests

    orig_batch_size = batch_size 
    if params.is_proxy == 0:   
        # Setting the url to check the concurrent ingest according to the streamer configuration
        if params.streamer == '':
            #params.url_num_ingests = "http://%s/get_session_state?id=0&reg_id=%s&edge_id=%s&first=0&last=0 " % (params.manager, Region_ID, Edge_ID)
            params.url_num_ingests = "http://%s/get_session_state?id=0&reg_id=%s&edge_id=0&first=0&last=0 " % (params.manager, Region_ID)
    
            
        else :
            params.url_num_ingests = "http://%s:5555/command/monitor_service?id=INGESTION_SESSIONS_IDS&opaque=" % (params.streamer)
    
    # Loop that will add more session in the end...
    orig_no_delay_sessions = params.no_delay_sessions
    #time_start_loop = time.time()
    while True:
    # Loop that will run on all ingests
        num = 0
        before_time = time.time()       
        while Real_index <  params.total_ingests:
            
            # checking for already existing sessions in streamer
            existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)
            if existing_ingests >= params.concurrent_ingests :
                time.sleep(5)
            #print "existing ingest=%s -- params_concurrent_ingests=%s -- params_total_ingests=%s -- Real_index=%s -- ingests_per_batch=%s, orig_per_batch=%s" %(existing_ingests, params.concurrent_ingests, params.total_ingests, Real_index,params.no_delay_sessions,orig_no_delay_sessions)
            while (existing_ingests < params.concurrent_ingests) and (Real_index <= params.no_delay_sessions) and ((Real_index - batch_size) < params.total_ingests) :
                
                if(batch_size == 0):
                    
                    if(params.concurrent_ingests >= params.total_ingests):
                        if (Real_index + batch_size > params.total_ingests):
                            batch_size = params.total_ingests - Real_index
                            #print "BATCH SIZE 1"
                    else:
                        if(Real_index + orig_batch_size > params.total_ingests) and not(((existing_ingests + orig_batch_size) > params.concurrent_ingests) and ((existing_ingests + orig_batch_size) > params.total_ingests)):
                            batch_size = params.total_ingests - Real_index
                            #print "BATCH SIZE 2"
                            #print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  the batch size " + str(batch_size) + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> 1" 
                        else:
                            if(existing_ingests + orig_batch_size) > params.concurrent_ingests:
                                batch_size = params.concurrent_ingests - existing_ingests
                                print "Real_index: " + str(Real_index) 
                                #print "BATCH SIZE 3 " + " params.concurrent_ingests: " + str(params.concurrent_ingests) + " existing_ingests: " + str(existing_ingests)
                                #print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  the batch size " + str(batch_size) + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> 2"
                            else:                             
                                batch_size = orig_batch_size
                                #print "BATCH SIZE 4"
                                #print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  the batch size " + str(batch_size) + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> 3"
                
                
                
                
                
                #channel calculation
                if (channel_counter == (channel_len )):
                    channel_counter = 0
               
                channel_multicast =  channels_list[channel_counter]
                
                if(params.rand_time == 1):
                    end_time = random.randint(params.start_time + 2 ,params.end_time)                    
                else:
                   end_time =  params.end_time
                # Calculate start time only on first loop
                if num == 0:                    
                #start time calculation
                    epoc_start_time =  time.time()                               
                    my_start_time = time.gmtime(epoc_start_time+params.start_time)
                    start_time = "%s-%s-%sT%s:%s:%sZ" % (my_start_time[0],my_start_time[1],my_start_time[2],my_start_time[3],my_start_time[4],my_start_time[5])
                if params.one_starting_time == 0:
                    epoc_start_time =  time.time()                               
                    my_start_time = time.gmtime(epoc_start_time+params.start_time)
                    start_time = "%s-%s-%sT%s:%s:%sZ" % (my_start_time[0],my_start_time[1],my_start_time[2],my_start_time[3],my_start_time[4],my_start_time[5])
                elif params.one_starting_time == 1:
                    pass
                                
                #end time calculation
                my_end_time = time.gmtime(epoc_start_time+end_time)
                end_time = "%s-%s-%sT%s:%s:%sZ" % (my_end_time[0],my_end_time[1],my_end_time[2],my_end_time[3],my_end_time[4],my_end_time[5])
                
                
                #fill single rec list
                single_rec_list = []
                single_rec_list.append(Real_index)
                single_rec_list.append(xml.sax.saxutils.escape(channel_multicast)) #xml.szx.saxutils --> Support escape chars in channel name
                single_rec_list.append(start_time)
                single_rec_list.append(end_time)
                single_rec_list.append(home_id)
                single_rec_list.append(stb_mac)                        
                recording_chunk_list.append(single_rec_list)
                
                if params.is_rsdvr_rev3==0:
                    rsdvr_rev='RSDVR'
                elif params.is_rsdvr_rev3==1:
                    rsdvr_rev='Rev3_RSDVR'
                elif params.is_rsdvr_rev3==2 or  params.is_rsdvr_rev3==3:
                    rsdvr_rev='v2'
                else:
                    print ' ---------------------------------- invalid RSDVR revision -----------------------------------'
                    
                if ((chunk_counter + 1) >= batch_size):
                    
                    #print "len: " + str(len(single_rec_list))
                    
                    if(params.open_sock_once == 0):                                               
                        RSDVRRecording(recording_chunk_list, batch_size, rsdvr_rev)
                    else:                        
                        RSDVRRecordingSockOnce(recording_chunk_list, batch_size, rsdvr_rev)
                    num += 1
                    #RSDVRRecording(recording_chunk_list, len(single_rec_list))
                    #print "\n\n*********Chunk was sent******* :" , recording_chunk_list
                    chunk_counter = 0
                    recording_chunk_list = []
                    single_rec_list = []
                    Real_index += batch_size
                    channel_counter += 1
                    if(params.ena_rec_per_sec != 1):
                        if params.sec_delay > 0 :
                            time.sleep(params.sec_delay)
                    existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)
                    #log.info("=" * 60 + "\n" + " " * 43 + "Total successful ingests so far = %d\n" % (params.success_ingests) + " " * 43 + "=" * 60)
                    #print "<<<<<<<<<<<<<<<<<<<<<<< REAL INDEX >>>>>>>>>>>>>>>>>>>>>>>>" +   str(Real_index)                  
                    # the case that ---->  existing_ingests + batch_size <= params.concurrent_ingests
                    
                    
                                                   
                else:
                    chunk_counter += 1
                
                if(params.concurrent_ingests >= params.total_ingests):
                    if (Real_index + batch_size > params.total_ingests):
                        batch_size = params.total_ingests - Real_index
                        #print "BATCH SIZE 1"
                else:
                    if(Real_index + orig_batch_size > params.total_ingests) and not(((existing_ingests + orig_batch_size) > params.concurrent_ingests) and ((existing_ingests + orig_batch_size) > params.total_ingests)):
                        batch_size = params.total_ingests - Real_index
                        #print "BATCH SIZE 2"
                        #print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  the batch size " + str(batch_size) + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> 1" 
                    else:
                        if(existing_ingests + orig_batch_size) > params.concurrent_ingests:
                            batch_size = params.concurrent_ingests - existing_ingests
                            print "Real_index: " + str(Real_index) 
                            #print "BATCH SIZE 3 " + " params.concurrent_ingests: " + str(params.concurrent_ingests) + " existing_ingests: " + str(existing_ingests)
                            #print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  the batch size " + str(batch_size) + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> 2"
                        else:                             
                            batch_size = orig_batch_size
                            #print "BATCH SIZE 4"
                            #print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  the batch size " + str(batch_size) + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>> 3"
                    
                   
                params.ingest_concurrent_counter += 1

                if((home_id_counter + 1) == params.num_home_id ):
                    home_id_counter = 0
                    mac_counter = (mac_counter + 1) % (params.num_stb_per_home)
                else:
                    home_id_counter += 1
                
                stb_mac = params.basic_mac + (home_id_counter * params.num_stb_per_home) + mac_counter 
                home_id = params.basic_home_id +  home_id_counter
                #print "Home ID: " + str(home_id)
                if(params.ena_rec_per_sec == 1):
                    if num % params.rec_per_sec == 0:
                        print "Delta time for 100 rec: %s" % str(time.time() - before_time) 
                        sleep_time = int(params.sec_delay) - (time.time() - before_time)
                        if sleep_time > 0:
                            time.sleep(sleep_time)
                        before_time = time.time()
                
                
                
                    
                    
            existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)                        
            params.no_delay_sessions += orig_no_delay_sessions  
            
        
        #time_end_loop = time.time()
        #print "Recording time>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>: " + str(time_end_loop - time_start_loop)
        ans = string.lower(raw_input("\nWould you like to add more RSDVR recordings? \n"))
        
        while (ans != 'y') and (ans != 'n'):
            ans = string.lower(raw_input("Wrong Input!!!\nWould you like to add more RSDVR recordings? (y/n): \n"))
            
        if ans == 'y':
            sess_tmp = int(raw_input("How many total live ingests?\n "))
            orig_no_delay_sessions = int(raw_input("How many recordings per batch would you like to add ?\n "))
            if sess_tmp > orig_no_delay_sessions:
                params.sec_delay = int(raw_input("How many Second delay between each batch ?\n "))
            params.total_ingests += sess_tmp
            if (params.num_home_id < orig_no_delay_sessions ):
                batch_size = params.num_home_id
            else:
                batch_size = orig_no_delay_sessions
            orig_batch_size = batch_size          
            #params.no_delay_sessions = Real_index + orig_no_delay_sessions -1
            continue
        elif ans == "n":
            break
        
        
    print_end_details()

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

if __name__ == "__main__":
    
    id = int(time.time()) + random.randint(0, 2147483648)
    # Getting current folder location
    #path = os.getcwd()
    path = "../"
    # Reading Configuration file
    config = ConfigObj(path+"/conf/config.ini")
    log_level = string.upper(config['Configuration']['desired_log_level'])
    
    #Globals
    params = globalParams()
    
    pars_INI_file(config)
    
    defineLogger()

    log = logging.getLogger('Ingest')
    
    #Getting Manager Version
    
    manager_version = get_manager_version(params.manager)
    #print "Manager version = %s\n" % (manager_version)
    version_num = stb_ip_parse(manager_version)
    if params.is_rsdvr_rev3==0:
        rsdvr_rev='RSDVR'
    elif params.is_rsdvr_rev3==1:
        rsdvr_rev='Rev3_RSDVR'
    elif params.is_rsdvr_rev3==2 or params.is_rsdvr_rev3==3:
        rsdvr_rev='v2'
    else:
        print ' ---------------------------------- invalid RSDVR revision -----------------------------------'
     
    if(params.open_sock_once == 1):
         manager_ip = params.manager[:string.find(params.manager,":")]
         manager_port = int(params.manager[string.find(params.manager,":") + 1:])
    #print "length --> ", length
    
         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         sock.settimeout(None)         
         sock.connect((manager_ip,manager_port)) 
                    
    if(params.add_recording_to_exist_env == 0 and params.is_rsdvr_rev3 != 3):
        CreateHomeIDs1(params.box_size, rsdvr_rev)
        if params.is_rsdvr_rev3 != 2 or params.is_rsdvr_rev3 != 3:
            CretaeSTBs(rsdvr_rev)
    else:
        pass
    check_if_manager_proxy()
    if(params.use_current_channels != 'y'):
        channels_list = GetChannelMapFromFile(params.channel_list_file,path)
    elif not ((params.is_rsdvr_rev3==2 and params.is_proxy ==1) or (params.is_rsdvr_rev3==3 and params.is_proxy ==1)):
        channels_list = GetChannelMapFromEnvironment(version_num)
    
    main()
    if(params.open_sock_once == 1):
        sock.close()
    
    #print "***" , channels_list
    
    
    
    
