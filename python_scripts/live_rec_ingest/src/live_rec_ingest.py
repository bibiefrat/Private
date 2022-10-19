#! /usr/bin/python

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
#import pexpect



class globalParams():
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
    
    params.manager = configFile['Configuration']['manager']
    params.streamer = configFile['Configuration']['streamer']
    params.multicast_addr = configFile['Configuration']['multicast_addr']
    params.multiple_source = configFile['Configuration']['multiple_source']
    params.one_fake_machine = int(configFile['Configuration']['one_fake_machine'])
    params.start_port = int(configFile['Configuration']['starting_port'])
    params.start_time = int(configFile['Configuration']['start_time'])
    params.end_time = int(configFile['Configuration']['end_time'])
    params.bandwidth = configFile['Configuration']['bandwidth']
    params.total_ingests = int(configFile['Configuration']['total_ingests'])
    params.concurrent_ingests = int(configFile['Configuration']['concurrent_ingests'])
    params.is_delay = configFile['Configuration']['delay_between_ingests']
    params.sec_delay = float(configFile['Configuration']['num_sec_delay'])
    params.log_file =  configFile['Configuration']['log_file_location']
    params.streamer_no_port = params.streamer[:string.find(params.streamer, ":")]
    params.no_delay_sessions = int(configFile['Configuration']['no_delay_sessions'])
    
    
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 

def print_open_details():
    global params
    if params.streamer == '' :
        log.info("=" * 60 + "\n" + " " * 43 + "Configuration details :\n" + " " * 43 + "   Manager is  : %s .\n" % (params.manager) + " " * 43 + "   Total Number of ingests to reach : %d .\n" % (params.total_ingests)    + " " * 43 + "=" * 60 )
        #print "num per batch-1 -->" , params.no_delay_sessions
    else :
        log.info("=" * 60 + "\n" + " " * 43 + "Configuration details :\n" + " " * 43 + "   Manager is  : %s .\n" % (params.manager) + " " * 43 + "   Streamer is : %s .\n" % (params.streamer) + " " * 43 + "   Total Number of ingests to reach : %d .\n" % (params.total_ingests) + " " * 43 + "   Number of concurrent ingests : %d .\n" %(params.concurrent_ingests) + " " * 43 + "=" * 60 )    

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def print_end_details():
    global params
    
    log.info("=!" * 30 + "\n" + " " * 43 + "Total successfull ingests allocation to the system =  %d\n" % (params.success_ingests) + " " * 43 + "Total failed ingests allocation to the system =  %d\n" % (params.failed_ingests) + " " * 43 + "end of script\n" + " " * 43 + "=!" * 30)
    

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Editing the XML for the Streamer load
def addByxPath(dom, xpath):               
    list = dom.xpathEval(xpath)
    for url in list:
        o = url.content
        #print "o in function-->" + o
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

    try:
        str_response = urllib2.urlopen(str_load)
        xml = str_response.read()
        dom = libxml2.parseDoc(xml)
        result = addByxPath(dom, "//X/total_load")
        log.info ("Streamer current load : %s %%" % (result))
    except urllib2.URLError, err:
        log.critical ("Couldn't get streamer load : %s " % (err.reason))
        
    

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def check_existing_ingests(url_num_Of_ingests, Ingest_Counter):

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
    
    
  #  log.info("=" * 60) + "\n" + " " *43 )
      #  log.info("Can not retrieve the number of concurrent ingests.\n" + " " *43 + "Manager did not respond .")
      #  log.info("Existing Concurrent ingests = %s" % (Ingests_Num))
      #  log.info("=" * 60)

    return Ingests_Num

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

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def CreateLiveRec(index, addr_and_port, start_time, end_time, bandwidth):
    # initializing the url responses for the exceptions
    global params

    #assetPath = urllib.quote_plus(assetPath.strip())
    #nameStart = urllib.quote_plus(str(nameStart))
    #nameEnd = urllib.quote_plus(str(nameEnd))
    #d = urllib.quote_plus(str(int(time.time()*100)))
    id = int(time.time()*1000)

    # Getting the ID from the manager
    #id = int(remote_date(params.manager))
    #print "id-->" + str(id)

    #time_id = int(((time.time()*1000) / 1000) + 10)
    time_id = int(((time.time()*1000) / 1000))

    #print "time_id-->" + str(time_id)
    nameStart = "live_"

    url =  "http://%s/update_rsdvr_session?update=0&type=-1&asset_id=%s_%s-%s&box_id=0&start_time=%s&end_time=%s&broadcast_addr=%s&bandwidth=%s&asset_type=0" % (params.manager, nameStart, index, id, (time_id+start_time), (time_id+start_time+end_time), urllib.quote_plus(addr_and_port), bandwidth )
    #print "url -->" + str(url) 

    try:

        response = urllib2.urlopen(url)
        xml = response.read()
        dom = libxml2.parseDoc(xml)
        #print "doc-->" + str(dom)
        result = addByxPath(dom, "//X/id")
        #print "result--->" + str(result)
        if result != "":
            log.info("=" * 60 + "\n" + " " * 43 + "Created live ingest number : %d\n" % (index) + " " * 43 + "Asset name : %s\n" % (result) + " " * 43 + "=" * 60 )                    
            #get_streamer_load(params.streamer)
            params.success_ingests += 1
            
        else:
            result = addByxPath(dom, "//X/id")
            log.error("*" * 60 + "\n" + " " * 43 + "Failed to create live ingest number : %d\n" % (index) + " " * 43 + "Error reason: %s\n" % (result) + " " * 43 + "*" * 60 )
            params.failed_ingests += 1
    except urllib2.URLError, err:
        log.critical ("*" * 60 + "\n" + " " * 43 + "Failed to create live ingest number : %d\n" % (index) + " " * 43 + "Manager error : %s\n" % (err.reason) + " " * 43 + "*" * 60 + "\n" )
        params.failed_ingests += 1
        
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def main():
    
    #Setting default timeout
    socket.setdefaulttimeout(30)
    
    global params
    

    # Getting the Manager version
    try :
        manager_ver_url = "http://%s/get_versions?X=0" % (params.manager)
        #print manager_ver_url
        manager_ver_open_url=urllib2.urlopen(manager_ver_url)
        manager_ver_response = manager_ver_open_url.read()
        manager_parse_ver = libxml2.parseDoc(manager_ver_response)
        manager_ver = addByxPath(manager_parse_ver, "//X/mngr_ver")
        CM_ver = addByxPath(manager_parse_ver, "//X/cm_ver")
        #print "manager version -->" + str(manager_ver)
    except :
        log.critical("=!" * 30 + "\n" + " " * 43 + "Manager didn't respond ...\n" + " " * 43 + "Script exit\n" + " " * 43 + "=!" * 30 )  
        sys.exit()
    
    version_num = stb_ip_parse(manager_ver)
            
    Ingest_Counter = 0 
    
    print_open_details()
    
    #Checking Region ID to receive concurrent ingests
    try:
            Region_ID_url = "http://%s/get_topology?X=0" % (params.manager)
            Region_result = urllib2.urlopen(Region_ID_url)
            xml_Region = Region_result.read()
            parse_region = libxml2.parseDoc(xml_Region)
            if manager_ver == '2.0.0.1':
                Region_ID = checkByxPath(parse_region, "//X/online/elem/base/id")
            elif ((version_num[0] == 2) and (version_num[1] == 0) and (version_num[3] > 12)) or (version_num[1] >= 5)  : 
                Region_ID = checkByxPath(parse_region, "//X/online/regions/elem/id")
            elif (version_num[0] >= 3) : 
                        Region_ID = checkByxPath(parse_region, "//X/online/regions/elem/id")
            else:
                Region_ID = checkByxPath(parse_region, "//X/online/elem/id")
                            
            #print "Region ID = " + str(Region_ID)
        
    except:
            print "Error while trying to get Region ID"
            print "url --> " + str(Region_ID_url)
            pass
    
    #Checking Edge ID to receive concurrent ingests
    try:
            Edge_ID_url = "http://%s/command/monitor_service?token=&agent=&id=TOPOLOGY&opaque=%s+DATA" % (params.manager, Region_ID)
            Edge_result = urllib2.urlopen(Edge_ID_url)
            xml_edge = Edge_result.read()
            parse_edge = libxml2.parseDoc(xml_edge)
            if manager_ver == '2.0.0.1':
                Edge_ID = checkByxPath(parse_edge, "//X/config/base/id")
            else:
                Edge_ID = checkByxPath(parse_edge, "//X/config/id")
                           
            #print "Edge ID = " + str(Edge_ID)
        
    except:
            print "Error while trying to get Edge ID"
            print "url --> " + str(Edge_ID_url)
            pass
        
    
    line_index = 0
    Real_index = 1
    
    # Setting the url to check the concurrent ingest according to the streamer configuration
    if params.streamer == '':
        #params.url_num_ingests = "http://%s/get_session_state?id=0&reg_id=%s&edge_id=%s&first=0&last=0 " % (params.manager, Region_ID, Edge_ID)
        params.url_num_ingests = "http://%s/get_session_state?id=0&reg_id=%s&edge_id=0&first=0&last=0 " % (params.manager, Region_ID)

        
    else :
        params.url_num_ingests = "http://%s:5555/command/monitor_service?id=INGESTION_SESSIONS_IDS&opaque=" % (params.streamer)
    
    # Loop that will add more session in the end...
    orig_no_delay_sessions = params.no_delay_sessions
    while True:
    # Loop that will run on all ingests
        #orig_no_delay_sessions = params.no_delay_sessions
        
        while Real_index <=  params.total_ingests:
            
            # checking for already existing sessions in streamer
            existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)
            print "existing ingest=%s -- params_concurrent_ingests=%s -- params_total_ingests=%s -- Real_index=%s -- ingests_per_batch=%s, orig_per_batch=%s" %(existing_ingests, params.concurrent_ingests, params.total_ingests, Real_index,params.no_delay_sessions,orig_no_delay_sessions)
            #while (existing_ingests < params.concurrent_ingests) and (existing_ingests <= params.total_ingests) and ((Real_index - 1) < params.total_ingests) :
            while (existing_ingests < params.concurrent_ingests) and (Real_index <= params.no_delay_sessions) and ((Real_index - 1) < params.total_ingests) :
                addr_and_port = "%s:%s" % (params.multicast_addr, params.start_port)
                
                CreateLiveRec(Real_index,addr_and_port, params.start_time, params.end_time, params.bandwidth)
            
                #if params.is_delay == "y":
                #    time.sleep(params.sec_delay)
    
                params.ingest_concurrent_counter += 1
                Real_index += 1

                if params.multiple_source == 'y' :            
                    if params.one_fake_machine == 1: # sending to incremental fake port
                        params.start_port += 1        
                    else : # Sending to incremental IP
                        fake_IP_nums = stb_ip_parse(params.multicast_addr)
                        print fake_IP_nums
                        if fake_IP_nums[3] > 253:
                            fake_IP_nums[3] = 0
                            fake_IP_nums[2] += 1 
                                            
                        #re-assemble the fake ip string           
                        fake_IP_nums[3] = int(fake_IP_nums[3])
                        fake_IP_nums[3] += 1
                        params.multicast_addr = str_stb_ip_parse(fake_IP_nums)
                        
            if existing_ingests < params.concurrent_ingests :
                params.no_delay_sessions += orig_no_delay_sessions  
                                
            log.info("=" * 60 + "\n" + " " * 43 + "Total successful ingests so far = %d\n" % (params.success_ingests) + " " * 43 + "=" * 60)
            if params.is_delay == "y":
                time.sleep(params.sec_delay)    
            
            existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)
        
        ans = string.lower(raw_input("\nWould you like to add more live ingests? \n"))
        return()
        while (ans != 'y') and (ans != 'n'):
            ans = string.lower(raw_input("Wrong Input!!!\nWould you like to add more live ingests? (y/n): \n"))
            
        if ans == 'y':
            sess_tmp = int(raw_input("How many total live ingests?\n "))
            orig_no_delay_sessions = int(raw_input("How many recordings per batch would you like to add ?\n "))
            params.total_ingests += sess_tmp
            params.no_delay_sessions = Real_index + orig_no_delay_sessions -1
            continue
        elif ans == "n":
            break
        
        
    print_end_details()

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

if __name__ == "__main__":

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
    
    main()
    
