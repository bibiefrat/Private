import urllib2
from configobj import ConfigObj
import os
import sys
import libxml2
import string
import logging
import signal
import xml.sax.saxutils
import urllib
import traceback
import time
import random
import subprocess
import shlex
import requests
import re

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
            sys.exit()
    finally:
        if manager_parse_ver:
            manager_parse_ver.freeDoc()
        
    return manager_ver



def addByxPath(dom, xpath):               
    list = dom.xpathEval(xpath)
    for url in list:
        o = url.content
        #print "o in function-->" +params.manager o
    return o


def stb_ip_parse(ip):
    
        ipNums = ip.split('.')
        ipNums[0] = int(ipNums[0]) 
        ipNums[1] = int(ipNums[1])
        ipNums[2] = int(ipNums[2])
        ipNums[3] = int(ipNums[3])
        
        return ipNums

def signal_handler(signal, frame):
    raise SystemExit

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

    formatter = logging.Formatter("[%(asctime)-19s] %(name)-8s: [%(levelname)s] %(message)26s", datefmt='%d-%m-%Y %H:%M:%S')
    logging.basicConfig(level=log_print,
                        format="[%(asctime)-19s] %(name)-8s: [%(levelname)s] %(message)26s",
                        datefmt='%d-%m-%Y %H:%M:%S',
                        filename=path+"/"+log_file,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(log_print)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    signal.signal(signal.SIGINT, signal_handler)


def defineReporter():
    # Defining the log for report file !
        
    formatter = logging.Formatter("[%(asctime)-19s] %(name)-8s: %(message)26s", datefmt='%d-%m-%Y %H:%M:%S')
    
    console = logging.FileHandler(path+"/log/report.log", 'w')
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    report = logging.getLogger('REPORT')
    report.addHandler(console)

    return report


def getElemVal(xml, location, name):
    start_pos = xml.find('>', xml.find(name, location)) + 1
    end_pos = xml.find('</' + name, start_pos)
    return xml[start_pos:end_pos].strip()


def get_boxes_list(manager,dom, xpath, all_list_asset, initial_box_num): 
    #print dom, xpath, all_list_asset
    global get_recordings
    global num_of_boxes
    #if bitrate :#print manager, xpath, initial_box_num, num_of_boxes
    list = dom.xpathEval("//X/boxes/elem/external_id")
    for node in list:
        all_boxes.append(node.content) 
        
    list = dom.xpathEval(xpath)
    if all_list_asset == 'y' :
        for node in list:
            #print "ALL BOXES"
            if use_bitrate == 'y' :
                if int(get_recordings) < total_bitrate :
                    if node.content != '0' :     
                        get_recordings = recordings_list(manager,node.content)
                        
            else :
                if node.content != '0' :       
                        get_recordings = recordings_list(manager,node.content)
                        
    else :
        if internal_initial_box_num == -1:
            print "No Initial home ID was found will Now Exit!!!"
            sys.exit(-1)
        else:
            pass 
        index=1
        for node in list:
            if use_bitrate == 'y' :
                if int(get_recordings) < total_bitrate :
                    if num_of_boxes > 0:
                        #print "node = %s, index = %s" % (node.content,index)
                        if (node.content != '0') and (int(node.content) >= int(initial_box_num)) : 
                            #print "****\nnode = " + str(node)       
                            get_recordings = recordings_list(manager,node.content)
                            index += 1
                            num_of_boxes -= 1
                            
                    else:
                        return 1           
            else:
                if num_of_boxes > 0:
                    #print "node = %s, index = %s" % (node.content,index)
                    if (node.content != '0') and (int(node.content) >= int(initial_box_num)) : 
                        #print "****\nnode = " + str(node)       
                        get_recordings = recordings_list(manager,node.content)
                        index += 1
                        num_of_boxes -= 1
                        
                else:
                    return 1        
    return 0      
                
def recordings_list(manager,node_content):

    global curr_bitrate
    rec_id_list = None
    if use_bitrate == 'y' :
        if curr_bitrate[0] + curr_bitrate[1] != 0 :
            "=!" * 30
            log.debug("*" * 80)
            log.debug("Total current bitrate =  %s Mb ---->  SD = %s Mb  ;  HD = %s Mb " % (round((curr_bitrate[0] + curr_bitrate[1]),3) , round(curr_bitrate[0],3), round(curr_bitrate[1],3)))
            log.debug("*" * 80 + "\n")
        if (curr_bitrate[0] + curr_bitrate[1]) < total_bitrate  :
            try:
                try :
                    # Opening the XML of the recordings per box
                    url = "http://%s/box_asset_list?id=%s&stb_addr=0" % (manager,urllib.quote_plus(node_content))
                    #print "url = " + url
                    all_rec_per_box = urllib2.urlopen(url)
                    xml = all_rec_per_box.read()
                    rec_id_list = libxml2.parseDoc(xml)
                    log.debug("Box ID  %s  with total bitrate of : " % (node_content))
                    curr_bitrate = get_recordings_per_boxes(manager,rec_id_list, "//X/elem/external_id")
                    
                    
                except urllib2.URLError, err:
                    print "Couldn't open URL for delete .\n url : %s . \n Manager Error : %s ." % (str(datarecv),err.reason)
            finally:
                if rec_id_list:
                    rec_id_list.freeDoc()
                
        return (curr_bitrate[0] + curr_bitrate[1])
    
    else :
        try:
            try :
                # Opening the XML of the recordings per box
                url = "http://%s/box_asset_list?id=%s&stb_addr=0" % (manager,urllib.quote_plus(node_content))
                #print "url = " + url
                all_rec_per_box = urllib2.urlopen(url)
                xml = all_rec_per_box.read()
                rec_id_list = libxml2.parseDoc(xml)
                curr_bitrate = get_recordings_per_boxes(manager,rec_id_list, "//X/elem/external_id")
                
            except urllib2.URLError, err:
                print "Couldn't open URL for delete .\n url : %s . \n Manager Error : %s ." % (str(datarecv),err.reason)
        finally:
            if rec_id_list:
                 rec_id_list.freeDoc()
    

def get_recordings_per_boxes(manager,dom, xpath):
    
    sd_bitrate_counter = 0.0 
    hd_bitrate_counter = 0.0
    is_str_in_name = 1   
    global temp_sd_bitrate 
    global temp_hd_bitrate  
    global num_sd
    global num_hd
    global duration
    global parameters_file
    global stop_recording
    all_asset_list=None
    #print manager, xpath,num_home_id     
    list = dom.xpathEval(xpath) 
    for node in list:
        #print node.content
        url = "http://%s/get_asset_properties?external_id=%s&internal_id=0" % (manager, urllib.quote_plus(node.content))
        #print url
        all_asset_info = urllib2.urlopen(url)
        xml = all_asset_info.read()
        #print xml
        all_asset_list = libxml2.parseDoc(xml)
        
        asset_state = int(get_info_asset(manager, all_asset_list, "/X/state"))
        asset_bitrate = float(get_info_asset(manager, all_asset_list, "/X/bandwidth")) / (1024 * 1024)
        asset_length = int(get_info_asset(manager, all_asset_list, "/X/act_duration"))
        asset_ready_time = (get_info_asset(manager, all_asset_list, "/X/ready_time"))
        asset_ready_time = asset_ready_time.split(".")[0]
        channel_raw = str(get_info_asset(manager, all_asset_list, "/X/ingested_from"))
        asset_state= str(get_info_asset(manager, all_asset_list, "/X/state"))
        #channel_name = channel_raw[8: channel_raw.find(",")]
        #channel_name = channel_raw[7:channel_raw.find(',')]
        #channel_name = channel_raw[8:channel_raw.rfind(",")]
        channel_name = channel_raw[8:]
        asset_name = node.content
        all_asset_list.freeDoc()
        if int(asset_state) != 0 :
            local_duration = asset_length
        else:
            local_duration = duration  
        #print "asset state = %s, asset_bitrate = %s" % (asset_state,asset_bitrate )
        if str_in_name == '':
            is_str_in_name = 1
        else: 
            if asset_name.rfind(str_in_name) > 0 :
                is_str_in_name = 1
            else:
                is_str_in_name = 0                
        
        
        if asset_state != 3 :
             if(is_str_in_name == 1):               
                if use_bitrate == 'y' :
                    #print "asset bitrate --> %s " % (asset_bitrate)
                    if (temp_sd_bitrate + temp_hd_bitrate + sd_bitrate_counter + hd_bitrate_counter) < total_bitrate :
                        if (asset_bitrate > 7.0) : # HD asset
                            if ((temp_hd_bitrate+hd_bitrate_counter) < (total_bitrate *  hd_ratio / 100 )) :
                                hd_bitrate_counter += asset_bitrate
                                parameters_file.write("%s 0 %s\n" % (node.content, local_duration))
                                num_hd += 1
                        else : # SD asset
                            if ((temp_sd_bitrate+sd_bitrate_counter) < (total_bitrate * (100 - hd_ratio) / 100 )) :
                                sd_bitrate_counter += asset_bitrate
                                parameters_file.write("%s 0 %s\n" % (node.content, local_duration))
                                num_sd += 1
                else :
                    if stop_recording != 2:
                        parameters_file.write("%s 0 %s\n" % (node.content, local_duration))
                    else:
                       r = re.compile('.*$.*$.*')
                       if r.match(node.content) == None:
                                home_id = node.content [node.content.find("$") + 1:node.content.rfind("$")]
                       else:
                                home_id = node.content [node.content.find("$") + 1:]
                       if node.content.find("_abr")!=-1 :
			                asset_id = node.content[:node.content.find("_abr")]
                       elif node.content.find("_cbr")!=-1 :
				            asset_id = node.content[:node.content.find("_cbr")]
                       else:
	                        #asset_id = node.content[2:node.content.find("$")]
                            asset_id = node.content[:node.content.find("$")]
                       url_start_time = "http://%s/search_rsdvr_assets?common_asset_id=%s&home_id=%s&state=0&max_items=1&offset=0&descending=1" % (manager, urllib.quote_plus(asset_id),str(home_id))
                       recording = urllib2.urlopen(url_start_time)
                       xml = recording.read()                       
                       record_info = libxml2.parseDoc(xml)
                       size = int(get_info_asset(manager, record_info, "/X/info/size"))
                       if (size >= 1):
                           start_time = (get_info_asset(manager, record_info, "/X/info/elem/recording/start_time"))
                           start_time =  str(start_time).split(".")
                           parameters_file.write("%s 0 %s %s %s %s\n" % (node.content, local_duration, asset_ready_time, channel_name, int(start_time[0])))
                       else:
                           url_start_time = "http://%s/search_rsdvr_assets?common_asset_id=%s&home_id=%s&state=4&max_items=1&offset=0&descending=1" % (manager, urllib.quote_plus(asset_id),str(home_id))
                           recording = urllib2.urlopen(url_start_time)
                           xml = recording.read()                       
                           record_info = libxml2.parseDoc(xml)
                           size = int(get_info_asset(manager, record_info, "/X/info/size"))
                           if (size >= 1):
                               start_time = int(get_info_asset(manager, record_info, "/X/info/elem/recording/start_time"))
                               parameters_file.write("%s 0 %s %s %s %s\n" % (node.content, local_duration, asset_ready_time, channel_name, start_time))                   
                        
             else:
                 pass
        #print "sd bitrate = %s, hd bitrate = %s" %(sd_bitrate_counter, hd_bitrate_counter )
    temp_sd_bitrate += sd_bitrate_counter
    temp_hd_bitrate += hd_bitrate_counter
    
    
     
    if use_bitrate == 'y' :
        log.debug("SD = %s Mb  ;  HD = %s Mb " %(round(sd_bitrate_counter,3), round(hd_bitrate_counter,3)))
        return [temp_sd_bitrate ,  temp_hd_bitrate]
   

def get_info_asset (manager, dom, xpath):
    
    list = dom.xpathEval(xpath)
    for node in list:
        r = node.content
        
    return r

def use_pltv(manager):
    
    url = "http://%s/get_all_pause_live?X=0" % (manager)
    all_pltv = urllib2.urlopen(url)
    pltv_xml = all_pltv.read()
    pltv_parse_temp = libxml2.parseDoc(pltv_xml)
    pltv_parse = pltv_parse_temp
    pltv_parse_temp.freeDoc()
    
    return pltv_parse

def get_pltv_asset (manager, dom, xpath):
    list = dom.xpathEval(xpath)
    for node in list:
        r = node.content
        pltv_assets_url = "http://%s/get_pause_live?max_items=10000&offset=0&common_asset_id=%s&descending=8" % (manager, urllib.quote_plus(r))
        pltv_asset_reply = urllib2.urlopen(pltv_assets_url)
        pltv_xml = pltv_asset_reply.read()
        pltv_asset_list = libxml2.parseDoc(pltv_xml)
        add_pltv_asset(manager, pltv_asset_list, "//X/recordings/info/elem/recording/external_id")                   
        pltv_asset_list.freeDoc()
    return

def add_pltv_asset (manager, dom, xpath):
    global duration
    global parameters_file
    
    list = dom.xpathEval(xpath)
    for node in list:
        extrenal_id = node.content
        pltv_state_url = "http://%s/get_asset_properties?external_id=%s&internal_id=0" % (manager, node.content)
        pltv_state_reply = urllib2.urlopen(pltv_state_url)
        pltv_state_xml = pltv_state_reply.read()
        pltv_state_list = libxml2.parseDoc(pltv_state_xml)
        pltv_get_state = int(get_info_asset(manager, pltv_state_list, "/X/state"))
        if pltv_get_state != 3 :
        
            during_ingest = node.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.content
            if during_ingest == "0" :
                duration = int(float(node.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.content))
            bitrate = node.next.next.next.next.next.next.next.next.next.next.next.next.next.next.content
            parameters_file.write("%s 0 %s\n" % (node.content, duration))
        pltv_state_list.freeDoc()   
    return

def checkByxPath(dom, xpath):   
                
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content

    return r

def get_internal_box_id(manager, dom, xpath, initial_box_num):  

    list = dom.xpathEval(xpath)
    for node in list:
        #print "<<<<<<<<<<<<< %s  >>>>>>>>>>>>>>" % str(node.content)
        if (node.content != 'NPVR') and (node.content != 'Pause') and (int(node.content) == initial_box_num) :
            #print "*******\ninternal ID --> %s\n********" % (node.prev.prev.prev.prev.prev.prev.content)
            return node.prev.prev.prev.prev.prev.prev.prev.prev.content
    return -1     

def StopRec():
    parameters_file = open("rsdvr_asset.list","r")
    asset_duration = "0"
    counter = 0 
    while asset_duration != '':
        asset_info = str(parameters_file.readline()).strip()    
        asset_duration = str.strip(asset_info[asset_info.rfind(' '):])
        asset_id = str.strip(asset_info[asset_info.find('_') + 1:asset_info.rfind('$')])       
        home_id =  str.strip(asset_info[asset_info.find('$') + 1:asset_info.find(' ')])  
        if asset_duration == '500000':
            counter += 1
            if use_proxy == 0:
                url = 'http://%s/Rev3_RSDVR?type=StopRecording&AssetID=%s&HomeID=%s' % (str(manager),str(asset_id),str(home_id))
            else:
                url = 'http://%s/Rev3_RSDVR?type=StopRecording&AssetID=%s&HomeID=%s' % (str(proxy),str(asset_id),str(home_id))
            urllib2.urlopen(url)
            print url
            time.sleep(0.05)
            #p = os.system("wget -q -b -o  /dev/null \"%s\" 1>/dev/null " % (url))
            #os.system("find . -name 'Rev3_RSDVR*'  | xargs rm" )
            #os.system('rm Rev3_RSDVR*')
            #time.sleep(0.0001)
    parameters_file.close()
    print counter

def UpdateRec():
    global num_of_update,update_mode,update_all_boxes,all_boxes,update_start_time,is_rsdvr_rev3
    recording_len = 10
    for j in range(num_of_update):
        parameters_file = open("rsdvr_asset.list","r")
        asset_duration = "0"
        counter = 0
        if update_all_boxes == 0:
            while asset_duration != '':
                asset_info = str(parameters_file.readline()).strip()
                if asset_info != "":
                    duration_start =   asset_info.find(' 0 ') + 1 
                    asset_duration = str.strip(asset_info[duration_start + 2: str.find(asset_info," " ,duration_start + 3)])
                    duration_end = str.find(asset_info," " ,duration_start + 3) + 2
                    recording_end_time = asset_info[duration_end - 1 : str.find(asset_info," ",duration_end +1)]
                    recording_end_time_index = str.find(asset_info," ",duration_end +1) +  2
                    call_sign = asset_info[recording_end_time_index - 1 :str.rfind(asset_info," ")]
                    if asset_info.find('_cbr') != -1:
                        asset_id = str.strip(asset_info[:asset_info.rfind('_cbr')])
                    elif asset_info.find('_abr') != -1:
                        asset_id = str.strip(asset_info[:asset_info.rfind('_abr')])
                    elif is_rsdvr_rev3 ==2:
                        asset_id = str.strip(asset_info[:asset_info.rfind('$')])
                    else:                    
                        asset_id = str.strip(asset_info[asset_info.find('_') + 1:asset_info.rfind('$')])                           
                    home_id =  str.strip(asset_info[asset_info.find('$') + 1:asset_info.find(' ')])
                    recording_start_time = asset_info[str.find(asset_info," ",int(recording_end_time_index) +1) + 1:]
                    #recording_start_time = recording_end_time
                    rec_duration = int(recording_end_time) - int(recording_start_time)
                    if j % 2 == 0:
                        rand = random.randint(int(-1 * 0.1 * rec_duration) , int(1 * 0.1 * rec_duration))
                    else:
                        pass
                    if (update_mode == 1):
                        recording_cur_end_time = int(recording_end_time) + rand
                    elif (update_mode == 0):
                        recording_cur_end_time = int(recording_end_time) + 10         
                    if asset_duration == '500000':
                        if is_rsdvr_rev3 !=2:
                            counter += 1
                            if use_proxy == 0:                
                                url =  'http://%s/Rev3_RSDVR?type=UpdateRecording&AssetID=%s&CallSign=%s&StartTime=%s&EndTime=%s&size=1&HomeID=%s'  % (str(manager),str(asset_id),str(call_sign),str(recording_start_time),str(recording_cur_end_time),str(home_id))
                            else:                
                                url =  'http://%s/Rev3_RSDVR?type=UpdateRecording&AssetID=%s&CallSign=%s&StartTime=%s&EndTime=%s&size=1&HomeID=%s'  % (str(proxy),str(asset_id),str(call_sign),str(recording_start_time),str(recording_cur_end_time),str(home_id))
                            urllib2.urlopen(url)
                            print url
                            time.sleep(0.05)
                        # is_rsdvr_rev3 == 2 
                        elif asset_info.find('_cbr') != -1 or asset_info.find('_abr') != -1 or  is_rsdvr_rev3 == 2:
                            print "update\n"
                            strart_rec= time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(float(recording_start_time)))
                            end_rec= time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(float(recording_cur_end_time)))
                            xml_msg = """<UpdateRecordingsTime>
         <ShowingID>%s</ShowingID>
        <EndTime>%s</EndTime>
        <Homes>
            <Home HomeID="%s"/>
        </Homes>
    </UpdateRecordingsTime>""" % (str(asset_id),str(end_rec),str(home_id))                            
                            headers = {'Content-Type' : 'text/x-xml2'}
                            requests.put('http://' + str(manager) + '/v2/recordings/', data=xml_msg, headers=headers)
                            
                        #p = os.system("wget -q -b -o  /dev/null \"%s\" 1>/dev/null " % (url))
                        #os.system("find . -name 'Rev3_RSDVR*'  | xargs rm" )
                        #os.system('rm Rev3_RSDVR*')
                        #time.sleep(0.0001)
                else:
                    break
        else: #update all boxes
            print all_boxes
            while asset_duration != '':
                asset_info = str(parameters_file.readline()).strip()
                if asset_info != "":
                    duration_start =   asset_info.find(' 0 ') + 1 
                    asset_duration = str.strip(asset_info[duration_start + 2: str.find(asset_info," " ,duration_start + 3)])
                    duration_end = str.find(asset_info," " ,duration_start + 3) + 2
                    recording_end_time = asset_info[duration_end - 1 : str.find(asset_info," ",duration_end +1)]
                    recording_end_time_index = str.find(asset_info," ",duration_end +1) +  2
                    call_sign = asset_info[recording_end_time_index - 1 :str.rfind(asset_info," ")]
                    if asset_info.find('_cbr') != -1:
                        asset_id = str.strip(asset_info[:asset_info.rfind('_cbr')])
                    elif asset_info.find('_abr') != -1:
                        asset_id = str.strip(asset_info[:asset_info.rfind('_abr')])
                    elif is_rsdvr_rev3 ==2:
                        asset_id = str.strip(asset_info[:asset_info.rfind('$')])                        
                    else:                    
                        asset_id = str.strip(asset_info[asset_info.find('_') + 1:asset_info.rfind('$')])
                    home_id =  str.strip(asset_info[asset_info.find('$') + 1:asset_info.find(' ')])
                    recording_start_time = asset_info[str.find(asset_info," ",int(recording_end_time_index) +1) + 1:]
                    #recording_start_time = recording_end_time
                    rec_duration = int(float(recording_end_time)) - int(float(recording_start_time))
                    if j % 4 == 0:
                        rand = random.randint(int(-1 * 0.1 * rec_duration) , int(1 * 0.1 * rec_duration))
                        rand1 = random.randint(0 , int(1 * 0.1 * rec_duration))
                    else:
                        pass
                    if (update_mode == 1):
                        recording_cur_end_time = int(recording_end_time) + rand
                        if update_start_time == 1:
                            recording_cur_start_time = int(recording_start_time) + rand1
                        else:
                            recording_cur_start_time = recording_start_time
                    elif (update_mode == 0):
                        recording_cur_end_time = int(recording_end_time) + 10  
                        if update_start_time == 1:
                            recording_cur_start_time = int(recording_start_time) + 10
                        else:
                            recording_cur_start_time = recording_start_time 
                               
                    if asset_duration == '500000':
                        counter += 1
                        if is_rsdvr_rev3 !=2:
                            if use_proxy == 0:
                                size = len(all_boxes)
                                url = 'http://%s/Rev3_RSDVR?type=UpdateRecording&AssetID=%s&CallSign=%s&StartTime=%s&EndTime=%s&size=%s' % (str(manager),str(asset_id),str(call_sign),str(recording_cur_start_time),str(recording_cur_end_time),str(size))
                                for i in range(size):
                                    url = url + '&HomeID=%s' % (str(all_boxes[i]))            
                                #url =  'http://%s/Rev3_RSDVR?type=UpdateRecording&AssetID=%s&CallSign=%s&StartTime=%s&EndTime=%s&size=1&HomeID=%s'  % (str(manager),str(asset_id),str(call_sign),str(recording_start_time),str(recording_cur_end_time),str(home_id))
                            else:
                                size = len(all_boxes)
                                url = 'http://%s/Rev3_RSDVR?type=UpdateRecording&AssetID=%s&CallSign=%s&StartTime=%s&EndTime=%s&size=%s' % (str(manager),str(asset_id),str(call_sign),str(recording_cur_start_time),str(recording_cur_end_time),str(size))
                                for i in range(size):
                                    url = url + '&HomeID=%s' % (str(all_boxes[i]))               
                                #url =  'http://%s/Rev3_RSDVR?type=UpdateRecording&AssetID=%s&CallSign=%s&StartTime=%s&EndTime=%s&size=1&HomeID=%s'  % (str(proxy),str(asset_id),str(call_sign),str(recording_start_time),str(recording_cur_end_time),str(home_id))
                            print url
                            urllib2.urlopen(url)
                            
                            time.sleep(0.05)
                            #p = os.system("wget -q -b -o  /dev/null \"%s\" 1>/dev/null " % (url))
                            #os.system("find . -name 'Rev3_RSDVR*'  | xargs rm" )
                            #os.system('rm Rev3_RSDVR*')
                            #time.sleep(0.0001)
                        elif asset_info.find('_cbr') != -1 or asset_info.find('_abr') != -1 or  is_rsdvr_rev3 ==2:
                            print "update\n"
                            strart_rec= time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(float(recording_cur_start_time)))
                            end_rec= time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(float(recording_cur_end_time)))
                            xml_msg = """<UpdateRecordingsTime>
         <ShowingID>%s</ShowingID>
        <EndTime>%s</EndTime>
        <Homes>
            <Home HomeID="%s"/>
        </Homes>
    </UpdateRecordingsTime>""" % (str(asset_id),str(end_rec),str(home_id))
                            headers = {'Content-Type' : 'text/x-xml2'}
                            requests.put('http://' + str(manager) + '/v2/recordings/', data=xml_msg, headers=headers)
                        
                        
                        
                else:
                    break            
            
            
            
        parameters_file.close()
        print counter
        recording_len = recording_len + 10
        time.sleep(2)
# ------------------------------------------------------
# Main

# Getting current folder location
#path = os.getcwd()
path = "../"

# Reading configuration file
config = ConfigObj(path+'/conf/config.ini')

asset_list_path = config['Configuration']['recording_list_path']
log_file = config['Configuration']['log_file']
log_level = string.upper(config['Configuration']['desired_log_level'])
manager = config['Configuration']['manager']
all_list_asset = config['Configuration']['all_list_asset']
asset_type = int(config['Configuration']['asset_type'])
pltv_location = int(config['Configuration']['pltv_location'])
initial_box_num = int(config['Configuration']['initial_box_num'])
num_of_boxes = int(config['Configuration']['num_of_boxes'])
use_bitrate = config['Configuration']['consider_bitrate']
total_bitrate = float(config['Configuration']['total_bitrate'])
hd_ratio = int(config['Configuration']['hd_ratio'])
str_in_name = str(config['Configuration']['str_in_name'])
use_db = int(config['Configuration']['use_db'])
db_addr = str(config['Configuration']['db_addr'])
stop_recording = int(config['Configuration']['stop_recording'])
use_proxy = int(config['Configuration']['use_proxy'])
proxy = config['Configuration']['proxy']
num_of_update = int(config['Configuration']['num_of_update'])
#----------------------------------------------------------------
get_recording = (config['Configuration']['get_recording'] == 'y')
get_ready = (config['Configuration']['get_ready'] == 'y')
update_mode =  int(config['Configuration']['update_mode'])
update_all_boxes  =  int(config['Configuration']['update_all_boxes'])
update_start_time = int(config['Configuration']['update_start_time'])
db_machine_password=str(config['Configuration']['db_machine_password'])
recording_num = int(config['Configuration']['recording_num'])
rand_shuffle = int(config['Configuration']['rand_shuffle'])
current_recording = int(config['Configuration']['current_recording'])
is_rsdvr_rev3 = int(config['Configuration']['is_rsdvr_rev3'])
db_order_by_external=int(config['Configuration']['db_order_by_external'])
db_type = str(config['Configuration']['db_type'])

#Assign default values for counters
all_boxes = []
temp_sd_bitrate = 0
temp_hd_bitrate = 0
num_sd = 0
num_hd = 0
curr_bitrate = [0,0]
get_recordings = 0
duration = 500000
internal_initial_box_num = -1

defineLogger()
log = logging.getLogger('Main')
# Deleting current rsdvr_asset.list file
try:
       
    x = os.path.exists("rsdvr_asset.list")
    if x == True :
        print "Removing old rsdvr_asset.list file...\n"
        z = os.remove(asset_list_path)
    else:
        print "File rsdvr_asset.list does not exist"

except:
    pass
manager_version = get_manager_version(manager)
print "Manager version = %s\n" % (manager_version)
version_num = stb_ip_parse(manager_version)

if ((version_num[0] == 3) and (version_num[1] < 5)) or (version_num[0] < 3):
    db_param="END_TIME"
elif ((version_num[0] == 3) and (version_num[1] >= 5)):
    db_param="EXT_CONTENT_END_TIME"
    
if not get_ready and not get_recording:
    print "Need to get at least one of recording assets and ready recorded assets"
    sys.exit(-1)

if use_bitrate == 'y':
    print "*" * 80 + "\nStarting to create RS-DVR asset list according the following requirements :\n    Total bitrate to reach = %s\n        HD bitrate = %s\n        SD bitrate = %s\n" %(total_bitrate, (float(hd_ratio) / 100 * total_bitrate), ((100.0 - float(hd_ratio)) / 100 * total_bitrate)) + "*" * 80 + "\n\n\n" 
else :
    print "Starting to create RS-DVR asset list...\n\n\n"

parameters_file = open("rsdvr_asset.list","w")



if asset_type != 2:
    # Opening the XML of the home_id's list
    url = "http://%s/get_boxes?offset=0&limit=100" % (manager)
    #print "url = " + url
    all_home_id = urllib2.urlopen(url)
    xml = all_home_id.read()
    home_id_list = libxml2.parseDoc(xml)
    #print "boxes-list -->" + str(home_id_list)
    
    # Get size of total boxes
    total_boxes_size = int(checkByxPath(home_id_list, "/X/total_count"))
    print "Total_number of boxes in the system : %s \n" % (total_boxes_size)
    # first active box internal ID
    list = home_id_list.xpathEval("//X/boxes/elem/id")
    for url in list:
        first_box_internal_id = url.content
        break;
  
    if use_db == 0:
        box_fetch = 100 
        for i in range (1 ,(total_boxes_size / 100) + 2) :
            if i == 1 :
                current_range = 0
            #finding internal ID of initial_box_number
            
            temp_internal_initial_box_num = get_internal_box_id(manager, home_id_list, "//X/boxes/elem/external_id", initial_box_num)
            if temp_internal_initial_box_num != -1 :
                internal_initial_box_num = temp_internal_initial_box_num            
            else:
                pass
            
            url = "http://%s/get_boxes?offset=%s&limit=100" % (manager, box_fetch)
            #print "url = " + url
            all_home_id = urllib2.urlopen(url)
            xml = all_home_id.read()
            home_id_list.freeDoc()
            home_id_list = libxml2.parseDoc(xml)
            current_range += 100
            box_fetch += 100
        home_id_list.freeDoc()
    else:
#    url = "http://%s/get_boxes?offset=0&limit=1&active=1&external_id=%s&mac_address=&service_group=0&only_overflowing=0" % (manager,initial_box_num)
#    #print "url = " + url
#    home_id_url = urllib2.urlopen(url)
#    xml = home_id_url.read()
#    home_id = libxml2.parseDoc(xml)
#    list = home_id.xpathEval("//X/boxes/elem/external_id")
#    for node in list:        #print "node = %s, index = %s" % (node.content,index)
#        if (node.content != '0') and (int(node.content) == int(initial_box_num)):
#            internal_initial_box_num_list =  home_id.xpathEval("//X/boxes/elem/id")
#            for node in internal_initial_box_num_list:
#                internal_initial_box_num = node.content
#        else:
#           print "Could not find the specified box"
#           break;
         if db_type == 'solid':         
             x = '''expect -c "set timeout -1;
             spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \'select id from rsdvr_box where active='1' and EXTERNAL_ID='%s'' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
             match_max 100000;
             expect *password:*;
             send -- %s\\r;
             interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows > rsdvr_asset.list  '''  % (str(db_addr),str(initial_box_num),str(db_machine_password))
             try:
                print x
                os.system(x)
             except:
                 traceback.print_exc(file=sys.stdout)
         elif db_type == 'postgres':
                x = '''expect -c "set timeout -1;
                spawn ssh %s -l root { export PGPASSWORD=fabrix ;psql -t -U fabrix -d manager -h %s -p 9999 -c \\" select id from rsdvr_box where active='1' and EXTERNAL_ID='%s'\\" exit; };
                match_max 100000;
                expect *password:*;
                send -- %s\\r;
                interact;"  |grep -v "export\|password\|psql" | grep '[0-9]*' > rsdvr_asset.list '''  % (str(db_addr),str(db_addr),str(initial_box_num),str(db_machine_password))                 
                
                
                print x
                try:
                    os.system(x)
                except:
                    traceback.print_exc(file=sys.stdout)         
             
             
         parameters_file.close()
         parameters_file = open("rsdvr_asset.list","r")
         internal_initial_box_num = str(parameters_file.readline()).strip()
         parameters_file = open("rsdvr_asset.list","w")
         parameters_file.write('')
         parameters_file.close()
         if internal_initial_box_num == '':
             print "Could not find initial_box_Num - exiting!!!!"
             exit()
         else:
            pass
    
    print "internal_initial_box_num = %s \n" % (internal_initial_box_num)
    
    if use_db == 0:    
        url = "http://%s/get_boxes?offset=0&limit=100" % (manager)
        #print "url = " + url
        all_home_id = urllib2.urlopen(url)
        xml = all_home_id.read()    
        home_id_list = libxml2.parseDoc(xml)
        
        
        #if total_boxes_size > 100 :
        #    print "Since there are %s boxes, The list
        box_fetch = 100 
        for i in range (1 ,(total_boxes_size / 100) + 2) :
            if i == 1 :
                current_range = 0
            print "Preparing asset list of boxes from : %s to %s out of %s" % (current_range, box_fetch, total_boxes_size)
            #Checking if PLTV assets are required
            if (asset_type == 0) :
                
                pltv_parsing = use_pltv(manager)
                
                if pltv_location == 0 : #Add PLTV assets in the beginning of the file
                    get_pltv_asset(manager,pltv_parsing, "//X/value/elem/common_asset_id")
               
            return_code = get_boxes_list(manager,home_id_list, "//X/boxes/elem/id", all_list_asset, internal_initial_box_num)
            if return_code ==1 :
               break
            else:
                pass     
            
            if (pltv_location == 1) and (asset_type != 1): #Add PLTV assets in the end of the file
                get_pltv_asset(manager,pltv_parsing, "//X/value/elem/common_asset_id")
            
            url = "http://%s/get_boxes?offset=%s&limit=100" % (manager, box_fetch)
            #print "url = " + url
            all_home_id = urllib2.urlopen(url)
            xml = all_home_id.read()
            home_id_list.freeDoc()
            home_id_list = libxml2.parseDoc(xml)
            
            current_range += 100
            box_fetch += 100
        home_id_list.freeDoc()
    else: ### we are using DB
        temp_internal_initial_box_num = internal_initial_box_num
        temp_internal_next_box_num = int(internal_initial_box_num) + 100
        
#         if all_list_asset == 'n':
#             x = '''expect -c "set timeout -1; 
#         spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \'select external_id,duration from asset where box_id in \(select id from rsdvr_box where external_id >= %s and active=1 \)  and box_id >0 and active=1 and error_code=0 order by box_id ' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
#         match_max 100000; 
#         expect *password:*; 
#         send -- %s\\r; 
#         interact;" | grep -i 2_ | sed -e 's/\([\!\_a-zA-Z0-9\.\$]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' >> rsdvr_asset.list'''  % (str(db_addr),str(initial_box_num),str(db_machine_password))    
#             print x
#             try:
#                 os.system(x)
#             except:
#                 traceback.print_exc(file=sys.stdout)
#         
        
        if all_list_asset == 'n' or recording_num != -1:
            if db_order_by_external == 0:
                if db_type == 'solid':
                    x  = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \'select id from rsdvr_box where active=1 and id>= \(select id from rsdvr_box where active=1 and external_id='%s'\) order by id limit %s' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows   '''  % (str(db_addr),str(initial_box_num),str(num_of_boxes),str(db_machine_password))
                    try:
                        print x
                        result = subprocess.check_output(x, shell=True)                
                    except:
                        traceback.print_exc(file=sys.stdout)
                 
                elif db_type == 'postgres':
                     x ='''expect -c "set timeout -1;
                spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \'select id from rsdvr_box where active=1 and id>= \(select id from rsdvr_box where active=1 and external_id='%s'\) order by id limit %s';sleep 1 \); done; exit;\\";
                match_max 100000;
                expect *password:*;
                send -- %s\\r;
                interact;"   |grep -v export | grep ' [0-9]* '   '''  % (str(db_addr),str(db_addr),str(initial_box_num),str(num_of_boxes),str(db_machine_password))
                     print x
                     try:
                        os.system(x)
                     except:
                        traceback.print_exc(file=sys.stdout)         
                         
                home_ids=','.join(shlex.split(result))
                
            elif db_order_by_external == 1:
                if db_type == 'solid':
                    x  = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select id from (select id,external_id from rsdvr_box where id>0 and active=1 and ascii(external_id)>=ascii('0') and ascii(external_id)<=ascii('9')) where CAST(external_id AS INTEGER) >= %s order by CAST(external_id AS INTEGER) limit %s\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows   '''  % (str(db_addr),str(initial_box_num),str(num_of_boxes),str(db_machine_password))
                    try:
                        print x
                        result = subprocess.check_output(x, shell=True)                
                    except:
                        traceback.print_exc(file=sys.stdout)
                elif db_type == 'postgres':
                     x = '''expect -c "set timeout -1;
                spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \'select id from rsdvr_box where id>0 and active=1 and CAST\(external_id AS INTEGER\) >= %s order by CAST\(external_id AS INTEGER\) limit %s';sleep 1 \); done; exit;\\";
                match_max 100000;
                expect *password:*;
                send -- %s\\r;
                interact;"    |grep -v "export\|password"  '''  % (str(db_addr),str(db_addr),str(initial_box_num),str(num_of_boxes),str(db_machine_password))
                     try:
                        print x
                        result = subprocess.check_output(x, shell=True)                
                     except:
                        traceback.print_exc(file=sys.stdout)                    
                
                
                home_ids=','.join(shlex.split(result))
                
                
                
                
            if db_type == 'solid':    
                x  = '''expect -c "set timeout -1;
             spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \'select external_id from rsdvr_box where active=1 and id>= \(select id from rsdvr_box where active=1 and external_id=%s\) order by id limit %s' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
             match_max 100000;
             expect *password:*;
             send -- %s\\r;
             interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows   '''  % (str(db_addr),str(initial_box_num),str(num_of_boxes),str(db_machine_password))
                try:
                    print x
                    result = subprocess.check_output(x, shell=True)                
                except:
                    traceback.print_exc(file=sys.stdout)  
                             
            elif db_type == 'postgres':
                 x = '''expect -c "set timeout -1;
                spawn ssh %s -l root { export PGPASSWORD=fabrix ;psql -t -U fabrix -d manager -h %s -p 9999 -c \\"select external_id from rsdvr_box where active=1 and id>= (select id from rsdvr_box where active=1 and external_id='%s') order by id limit %s\\"; exit; };
                match_max 100000;
                expect *password:*;
                send -- %s\\r;
                interact;"   |grep -v "export\|password" '''  % (str(db_addr),str(db_addr),str(initial_box_num),str(num_of_boxes),str(db_machine_password))
                 print x
                 try:
                    print x
                    result = subprocess.check_output(x, shell=True)                
                 except:
                    traceback.print_exc(file=sys.stdout)                
                            
            
            all_boxes = shlex.split(result)
            
            
            if current_recording == -1 and stop_recording != 2:
                if db_type == 'solid':                
                    x = '''expect -c "set timeout -1; 
                spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 order by id limit %s' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                match_max 100000; 
                expect *password:*; 
                send -- %s\\r; 
                interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(home_ids),str(recording_num),str(db_machine_password))    
                    print x
                    try:
                        os.system(x)
                    except:
                        traceback.print_exc(file=sys.stdout) 
                elif db_type == 'postgres':
                     x = '''expect -c "set timeout -1;
                    spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \'select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 order by id limit %s';sleep 1 \); done; exit;\\";
                    match_max 100000;
                    expect *password:*;
                    send -- %s\\r;
                    interact;"   |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(db_addr),str(home_ids),str(recording_num),str(db_machine_password))
                     print x
                     try:
                        os.system(x)
                     except:
                        traceback.print_exc(file=sys.stdout)          
 
                       
            elif stop_recording != 2 and (current_recording == 1 or  current_recording == 2 or current_recording == 3 or current_recording == 0):
                if stop_recording != 2 and current_recording == 1:
                    if db_type == 'solid':        
                        x = '''expect -c "set timeout -1; 
                spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 and A.ingesting=%s order by id limit %s' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                match_max 100000; 
                expect *password:*; 
                send -- %s\\r; 
                interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(home_ids),str(current_recording),str(recording_num),str(db_machine_password))    
                        print x
                        try:
                            os.system(x)
                        except:
                            traceback.print_exc(file=sys.stdout)
                    elif db_type == 'postgres':
                         x = '''expect -c "set timeout -1;
                        spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \'select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 and A.ingesting=%s order by id limit %s';sleep 1 \); done; exit;\\";
                        match_max 100000;
                        expect *password:*;
                        send -- %s\\r;
                        interact;"   |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(db_addr),str(home_ids),str(current_recording),str(recording_num),str(db_machine_password))
                         print x
                         try:
                            os.system(x)
                         except:
                            traceback.print_exc(file=sys.stdout)          

                                         
                elif stop_recording != 2 and (current_recording == 3 or current_recording == 2):
                    if current_recording == 3:
                        sign = '<'
                    elif current_recording == 2:
                        sign = '>'
                    if db_type == 'solid':
                        x = '''expect -c "set timeout -1; 
                spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id, live_recording_session rs where rs.asset_internal=A.data_id and B.id in (%s) and B.active=1 and A.active=1 and A.ingesting=1 and (CASE WHEN start_time >creation_time then start_time else creation_time end) %s timestampadd(3,-2,now()) order by B.id limit %s' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                match_max 100000; 
                expect *password:*; 
                send -- %s\\r; 
                interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(home_ids),str(sign),str(recording_num),str(db_machine_password))    
                        print x
                        try:
                            os.system(x)
                        except:
                            traceback.print_exc(file=sys.stdout)
                    elif db_type == 'postgres':        
                         x = '''expect -c "set timeout -1;
                        spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \'select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id, live_recording_session rs where rs.asset_internal=A.data_id and B.id in (%s) and B.active=1 and A.active=1 and A.ingesting=1 and (CASE WHEN start_time >creation_time then start_time else creation_time end) %s timestampadd(3,-2,now()) order by B.id limit %s';sleep 1 \); done; exit;\\";
                        match_max 100000;
                        expect *password:*;
                        send -- %s\\r;
                        interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(db_addr),str(home_ids),str(sign),str(recording_num),str(db_machine_password))
                         print x
                         try:
                            os.system(x)
                         except:
                            traceback.print_exc(file=sys.stdout)                               
                 
                 
                elif stop_recording != 2 and current_recording == 0:
                        if db_type == 'solid':
                            x = '''expect -c "set timeout -1; 
                spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id, live_recording_session rs where rs.asset_internal=A.data_id and B.id in (%s) and B.active=1 and A.active=1 and A.ingesting=0 and A.error_code=0 order by B.id limit %s' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                match_max 100000; 
                expect *password:*; 
                send -- %s\\r; 
                interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(home_ids),str(recording_num),str(db_machine_password))    
                            print x
                            try:
                                os.system(x)
                            except:
                                traceback.print_exc(file=sys.stdout)
                        elif db_type == 'postgres':
                             x = '''expect -c "set timeout -1;
                            spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \'select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id, live_recording_session rs where rs.asset_internal=A.data_id and B.id in (%s) and B.active=1 and A.active=1 and A.ingesting=0 and A.error_code=0 order by B.id limit %s';sleep 1 \); done; exit;\\";
                            match_max 100000;
                            expect *password:*;
                            send -- %s\\r;
                            interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(db_addr),str(home_ids),str(recording_num),str(db_machine_password))
                             print x
                             try:
                                os.system(x)
                             except:
                                traceback.print_exc(file=sys.stdout)                                              
                           
            
                                            
            elif stop_recording == 2:
                    if db_type == 'solid':
                        x = '''expect -c "set timeout -1; 
        spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select min(RS.external_id), 0 , 500000, TIMESTAMPDIFF(1,'1970-1-1 00:00',max(%s)) as ready_time, min(CH.name) channel, timestampdiff(1, '1970-1-1 00:00', min(case when CREATION_TIME<start_time then creation_time else start_time end)) as start_time_  from live_recording_session RS, multicast_channel CH,rsdvr_box BOX, asset where asset.data_id=RS.asset_internal and  RS.box_id=BOX.id and multicast_channel=CH.id and BOX.active=1 and RS.active=1 and ingesting=1 and BOX.external_id<>'NPVR' and BOX.active=1 and BOX.id in  (%s) group by BOX.id,RS.common_asset_id\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
        match_max 100000; 
        expect *password:*; 
        send -- %s\\r; 
        interact;"  | grep -v NULL |sed '/^\s*$/d'| grep -v "spawn\|password"  |tr -s ' ' > rsdvr_asset.list'''  % (str(db_addr),str(db_param),str(home_ids),str(db_machine_password))
                
                        print x
                        try:
                            os.system(x)
                        except:
                            traceback.print_exc(file=sys.stdout)
                    elif db_type == 'postgres':
                             x = '''expect -c "set timeout -1;
                             spawn ssh %s -l root { export PGPASSWORD=fabrix ;psql -t -U fabrix -d manager -h %s -p 9999 -c \\"select min(RS.external_id), 0 , 500000, EXTRACT(EPOCH FROM max(%s)) as ready_time, min(CH.name) channel, EXTRACT(EPOCH FROM min(case when CREATION_TIME<start_time then creation_time else start_time end)) as start_time_  from live_recording_session RS, multicast_channel CH,rsdvr_box BOX, asset where asset.data_id=RS.asset_internal and  RS.box_id=BOX.id and multicast_channel=CH.id and BOX.active=1 and RS.active=1 and ingesting=1 and BOX.external_id<>'NPVR' and BOX.active=1 and BOX.id in  (%s) group by BOX.id,RS.common_asset_id\\"; exit; };
                            match_max 100000;
                            expect *password:*;
                            send -- %s\\r;
                            interact;"|grep -v "export\|password" | tr -s " " | tr '|' ' '  |  tr -s " " > rsdvr_asset.list'''  % (str(db_addr),str(db_addr),str(db_param),str(home_ids),str(db_machine_password))
                             print x
                             try:
                                os.system(x)
                             except:
                                traceback.print_exc(file=sys.stdout)                                         
                                            
                      
            if  stop_recording != 2 and (all_list_asset != 'n' or recording_num == -1): # the bellow is relevant if we are not updating recordings end time    
                if rand_shuffle == 1 and recording_num != -1:
                    if current_recording == -1:
                        if db_type == 'solid':
                            x = '''expect -c "set timeout -1; 
                    spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 and error_code=0 order by id limit -1' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                    match_max 100000; 
                    expect *password:*; 
                    send -- %s\\r; 
                    interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(home_ids),str(db_machine_password))    
                            print x
                            try:
                                os.system(x)
                            except:
                                traceback.print_exc(file=sys.stdout)
                        elif db_type == 'postgres':
                             x = '''expect -c "set timeout -1;
                            spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 and error_code=0 order by id limit -1';sleep 1 \); done; exit;\\";
                            match_max 100000;
                            expect *password:*;
                            send -- %s\\r;
                            interact;"   |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(db_addr),str(home_ids),str(db_machine_password))
                             print x
                             try:
                                os.system(x)
                             except:
                                traceback.print_exc(file=sys.stdout)                             
                            
                        
                    elif current_recording != -1:
                        if db_type == 'solid':
                            x = '''expect -c "set timeout -1; 
                    spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 and A.ingesting=%s order by id limit -1' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                    match_max 100000; 
                    expect *password:*; 
                    send -- %s\\r; 
                    interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(home_ids),str(current_recording),str(db_machine_password))    
                            print x
                            try:
                                os.system(x)
                            except:
                                traceback.print_exc(file=sys.stdout)
                        elif db_type == 'postgres':
                             x = '''expect -c "set timeout -1;
                            spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 and A.ingesting=%s order by id limit -1';sleep 1 \); done; exit;\\";
                            match_max 100000;
                            expect *password:*;
                            send -- %s\\r;
                            interact;"   |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' > rsdvr_asset.list'''  % (str(db_addr),str(db_addr),str(home_ids),str(current_recording),str(db_machine_password))
                             print x
                             try:
                                os.system(x)
                             except:
                                traceback.print_exc(file=sys.stdout)                                      
                            
                            
                            
                                                
                    lines = open('rsdvr_asset.list',"r").readlines()
                    print lines
                    v=random.shuffle(lines)                
                    print lines                    
                    open('rsdvr_asset.list', 'w').writelines(lines)                             
                    f = open("rsdvr_asset.list","r")
                    lines = f.readlines()
                    print "------>"  + str(lines)
                    f.close()                
                    f = open("rsdvr_asset.list","w")
                    count = 0
                    for line in lines:
                        if count < int(recording_num):                       
                            f.write(line)
                            print line
                        else:                        
                            break
                        count += 1                    
                    print count
                    f.close()
                if rand_shuffle == 1 and recording_num == -1:
                     lines = open('rsdvr_asset.list').readlines()
                     random.shuffle(lines)
                     open('rsdvr_asset.list', 'w').writelines(lines)
            #         if all_list_asset == 'n':
            #             num_of_boxes = total_boxes_size
            #             temp_internal_initial_box_num = first_box_internal_id
            #             temp_internal_next_box_num = int(first_box_internal_id) + 100
            #             internal_initial_box_num = first_box_internal_id
            #             x = '''expect -c "set timeout -1; 
            #     spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \'select box_id from asset where active=1 and error_code=0 and box_id <> '0' order by box_id desc LIMIT 1' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
            #     match_max 100000; 
            #     expect *password:*; 
            #     send -- %s\\r; 
            #     interact;" | grep -i '  [0-9]* ' | grep -v 'BOX_ID' | grep -v '\\-\\-' | sed -e 's/[\\s]*^//' > rsdvr_asset.list  '''  % (str(db_addr),str(db_machine_password))
            #             
            #             print x
            #             try:
            #                 os.system(x)
            #             except:
            #                 traceback.print_exc(file=sys.stdout)
            #             parameters_file.close()
            #             parameters_file = open("rsdvr_asset.list","r")
            #             last_box_id = str(parameters_file.readline()).strip()
            #             #print last_box_id
            #             num_of_boxes = int(last_box_id) - int(first_box_internal_id) + 1
            #             parameters_file.close()
            #             parameters_file = open("rsdvr_asset.list","w")
            #             parameters_file.write('')
            #             parameters_file.close()
            #             
            #         
            #             if num_of_boxes < 100:
            #               temp_internal_next_box_num =   int(temp_internal_initial_box_num) + num_of_boxes
            #             
            #             while int(internal_initial_box_num) + int(num_of_boxes) >= int(temp_internal_next_box_num):
            #                 print "Adding assets of boxes with internal ID's: %s -> %s" % (str(temp_internal_initial_box_num), str(temp_internal_next_box_num))
            #                 x = '''expect -c "set timeout -1; 
            #         spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \'select external_id,duration from asset where box_id>=%s AND box_id<%s and active=1 and error_code=0 order by box_id' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
            #         match_max 100000; 
            #         expect *password:*; 
            #         send -- %s\\r; 
            #         interact;" | grep -i 2_ | sed -e 's/\([\!\_a-zA-Z0-9\.\$]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' >> rsdvr_asset.list'''  % (str(db_addr),str(temp_internal_initial_box_num),str(temp_internal_next_box_num),str(db_machine_password))
            #                 
            #                 print x
            #                 os.system(x)
            #                 temp_internal_initial_box_num = int(temp_internal_initial_box_num) + 100    
            #                 temp_internal_next_box_num = int(temp_internal_next_box_num) + 100
            
        if all_list_asset == 'y':
            num_of_boxes = total_boxes_size
            temp_internal_initial_box_num = first_box_internal_id
            temp_internal_next_box_num = int(first_box_internal_id) + 100
            internal_initial_box_num = first_box_internal_id
            if stop_recording != 2:
                if db_type == 'solid':
                    x = '''expect -c "set timeout -1; 
        spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \'select external_id,duration from asset where box_id>0  and active=1 and error_code=0 order by box_id' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
        match_max 100000; 
        expect *password:*; 
        send -- %s\\r; 
        interact;"  |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' >> rsdvr_asset.list'''  % (str(db_addr),str(db_machine_password))
                elif db_type == 'postgres':
                    x = '''expect -c "set timeout -1;
                            spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 and A.ingesting=%s order by id limit -1';sleep 1 \); done; exit;\\";
                            match_max 100000;
                            expect *password:*;
                            send -- %s\\r;
                            interact;"   |sed '/^\s*$/d'| grep -v "spawn\|password" | sed -e 's/\([\!\_a-zA-Z0-9\.\$\-]*\)\s*\([0-9]*\)/\\1 0 \\2/' | sed -e 's/\.[0-9]*/ /' | sed -e 's/ 0 0/ 0 500000/' >> rsdvr_asset.list'''  % (str(db_addr),str(db_machine_password))
                                                
        
            else:
                if db_type == 'solid':
                    x = '''expect -c "set timeout -1; 
        spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select min(RS.external_id), 0 , 500000, TIMESTAMPDIFF(1,'1970-1-1 00:00',max(EXT_CONTENT_END_TIME)) as ready_time, min(CH.name) channel, timestampdiff(1, '1970-1-1 00:00', min(case when CREATION_TIME<start_time then creation_time else start_time end)) as start_time_  from live_recording_session RS, multicast_channel CH,rsdvr_box BOX, asset where asset.data_id=RS.asset_internal and  RS.box_id=BOX.id and multicast_channel=CH.id and BOX.active=1 and RS.active=1 and ingesting=1 and BOX.external_id<>'NPVR' and BOX.active=1 group by BOX.id,RS.common_asset_id\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
        match_max 100000; 
        expect *password:*; 
        send -- %s\\r; 
        interact;"  | grep -v NULL |sed '/^\s*$/d'| grep -v "spawn\|password"  |tr -s ' ' >> rsdvr_asset.list'''  % (str(db_addr),str(db_param),str(db_machine_password))
                elif db_type == 'postgres':
                    x = '''expect -c "set timeout -1;
                            spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \' select A.external_id,A.duration from rsdvr_box B left join asset A on B.id=A.box_id where id in (%s) and B.active=1 and A.active=1 and A.ingesting=%s order by id limit -1';sleep 1 \); done; exit;\\";
                            match_max 100000;
                            expect *password:*;
                            send -- %s\\r;
                            interact;"   | grep -v NULL |sed '/^\s*$/d'| grep -v "spawn\|password"  |tr -s ' ' >> rsdvr_asset.list'''  % (str(db_addr),str(db_addr),str(db_param),str(db_machine_password))
                                                                    
                
                
            print x
            try:
                os.system(x)
            except:
                traceback.print_exc(file=sys.stdout)
            parameters_file.close()    
            
            
            
            
            
            
            
            
else : # Only PLTV assets OR RSDVR & PLTV (end of file)    
    #parameters_file = open("rsdvr_asset.list","a")
    
    pltv_parsing = use_pltv(manager)
    get_pltv_asset(manager,pltv_parsing, "//X/value/elem/common_asset_id")
               
parameters_file.close()

if use_bitrate == 'y' :
    log.info("\n\n\nFinished creating RS-DVR asset list file with : \n\n SD assets : %s  with total bitrate of : %s\n HD assets : %s  with total bitrate of : %s\n\nTotal bitrate : %s\n\nPlease use \"rsdvr_asset.list\" as your asset list \n\n\n" % (num_sd, round(temp_sd_bitrate,3), num_hd, round(temp_hd_bitrate,3), round(temp_sd_bitrate+temp_hd_bitrate,3)))
else :
    log.info("\n\n\nFinished creating RS-DVR asset list file .\nPlease use \"rsdvr_asset.list\" as your asset list \n\n\n")

if stop_recording ==1:
    StopRec ()
elif stop_recording == 2:
    UpdateRec ()

