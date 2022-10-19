from configobj import ConfigObj
import libxml2
import logging
import os
import random
import signal
import string
import sys
import time
import urllib2
import socket

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


def get_info_asset (manager, dom, xpath):
    
    list = dom.xpathEval(xpath)
    for node in list:
        r = node.content
    
    return r


def get_internal_box_id(manager, dom, xpath, initial_box_num):  

    list = dom.xpathEval(xpath)
    for node in list:
        if (node.content != 'NPVR') and (node.content != 'Pause') and (int(node.content) == initial_box_num) :
            #print "*******\ninternal ID --> %s\n********" % (node.prev.prev.prev.prev.prev.prev.content)
            return node.prev.prev.prev.prev.prev.prev.content
        
        

def get_boxes_list(manager,dom, xpath, all_list_asset, initial_box_num, num_of_boxes): 
    

    
    list = dom.xpathEval(xpath)    
    if all_list_asset == 'y' :
        for node in list:
           if (node.content != '0') and (node.content != '1') :     
               recordings_list(manager,node.content,node.next.next.next.next.next.next.content)
        
    else :
    
        index=1
        for node in list:
            if index <= num_of_boxes:
                #print "node = %s, index = %s" % (node.content,index)
                if (node.content != '0') and (node.content != '1') and (int(node.content) >= int(initial_box_num)) : 
                    #print "****\nnode = " + str(node)       
                    recordings_list(manager,node.content,node.next.next.next.next.next.next.content)
                    index += 1            


def recordings_list(manager,node_content,home_id):

    try :
        # Opening the XML of the recordings per box
        url = "http://%s/box_asset_list?id=%s&stb_addr=0" % (manager,node_content)
        #print "url = " + url
        all_rec_per_box = urllib2.urlopen(url)
        xml = all_rec_per_box.read()
        rec_id_list = libxml2.parseDoc(xml)

        stop_recording_per_boxes_POST(manager,rec_id_list, "//X/elem/external_id",home_id)

    except urllib2.URLError, err:
        print "Couldn't open URL for delete .\n url : %s . \n Manager Error : %s ." % (str(datarecv),err.reason)
        
    return ()

def stop_recording_per_boxes_POST (manager,dom, xpath,home_id):
    
 

    global success_ingests
    global failed_ingests 

    
    counter = 0

    
      
    list = dom.xpathEval(xpath)
    for node in list:
        
        msg = '<?xml version="1.0" encoding="utf-8"?>'
        #print node.content
        url = "http://%s/get_asset_properties?external_id=%s&internal_id=0" % (manager, node.content)
        #print url
        all_asset_info = urllib2.urlopen(url)
        xml = all_asset_info.read()
        all_asset_list = libxml2.parseDoc(xml)
        
        real_asset_state = int(get_info_asset(manager, all_asset_list, "/X/state"))
        print "asset = %s , state = %s" % (node.content, real_asset_state)
        
        
        asset_id = node.content[2:string.find(node.content, "$")]
        if  real_asset_state == 0:
            msg += '<StopRecording  AssetID="%s" HomeID="%s" MACAddress="102030405060">' % (str(asset_id), str(home_id)) 
            counter += 1

        
               
    
            msg += '</StopRecording>'
    
            print "send xml:\n" + msg
            print_errors=int(1)
    
            manager_ip = manager[:string.find(manager,":")]
            manager_port = int(manager[string.find(manager,":") + 1:])
            length=len(msg)  
            #print "length --> ", length
    
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            initial_time = time.time()
            s.connect((manager_ip,manager_port )) 
            time_after_connect = time.time()
            connect_time = time_after_connect - initial_time
            print "Connect time : %s\n" % (connect_time)
            s.send("POST /%s HTTP/1.0\r\n" % (rsdvr_rev))
            s.send("Content-Type: text/xml\r\n")
            s.send("Content-Length: "+str(length)+"\r\n\r\n")

            try : 
                s.sendall(msg)
                time_after_send_msg = time.time()
                msg_send_time = time_after_send_msg - initial_time
                if msg_send_time > print_errors :
                    print "Sending msg time : %s long time\n" % (msg_send_time)
                else:
                        print "Sending msg time : %s\n" % (msg_send_time)
          
                        datarecv=s.recv(1024)
                        print "Reply Received: "+ str(datarecv)
                if (str(datarecv).find("HTTP/1.0 200 OK") != -1):
                    success_ingests += counter
                    counter=0
                else:
                    failed_ingests += counter
                    counter=0
    
            except socket.error,message :
                  print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n MSG was not sent due to the following socket error : %s \n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n " % (str(message))
    
            s.close()
            time_after_closing_socket = time.time()
            close_socket_time = time_after_closing_socket - initial_time
            print "Closing socket time : %s\n" % (close_socket_time)
    
        
            
    print "Number of stopped recordings is %s" % (success_ingests)     
    return 







#Main
################################################
#define_global
success_ingests = 0
failed_ingests = 0 

# Getting current folder location
path = "../"

# Reading configuration file
config = ConfigObj(path+'/conf/config.ini')

log_file = config['Configuration']['log_file']
log_level = string.upper(config['Configuration']['desired_log_level'])
manager = config['Configuration']['manager']
all_list_asset = config['Configuration']['all_list_asset']
initial_box_num = int(config['Configuration']['initial_box_num'])
num_of_boxes = int(config['Configuration']['num_of_boxes'])
is_rsdvr_rev3 = int(str(config['Configuration']['is_rsdvr_rev3']).strip())

if is_rsdvr_rev3==0:
    rsdvr_rev='RSDVR'
elif is_rsdvr_rev3==1:
    rsdvr_rev='Rev3_RSDVR'
else:
    print ' ---------------------------------- invalid RSDVR revision -----------------------------------'


#get_box_list

url = "http://%s/boxes_list?X=0" % (manager)
print "url = " + url
all_home_id = urllib2.urlopen(url)
xml = all_home_id.read()
home_id_list = libxml2.parseDoc(xml)


#finding internal ID of initial_box_number
internal_initial_box_num = get_internal_box_id(manager, home_id_list, "//X/elem/external_id", initial_box_num)
#print "internal_initial_box_num = ", internal_initial_box_num
get_boxes_list(manager,home_id_list, "//X/elem/id", all_list_asset, internal_initial_box_num, num_of_boxes)           
            
            
            
            