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
import lxml.builder as lb
from lxml import etree



class globalParams():
    def __init__(self):
        self.success_ingests = 0
        self.failed_ingests = 0
        self.ingest_concurrent_counter = 1
        self.manager = ""
        self.streamer = ""
        self.streamer_no_port = ""
        self.url_num_ingests = ""
        self.max_sessions = ""
        self.concurrent_ingests = ""
        self.assets_file = ""
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
    params.max_sessions = int(configFile['Configuration']['total_ingests'])
    params.concurrent_ingests = int(configFile['Configuration']['concurrent_ingests'])
    params.is_delay = configFile['Configuration']['delay_between_ingests']
    params.sec_delay = float(configFile['Configuration']['num_sec_delay'])
    params.assets_file = configFile['Configuration']['asset_file_location']
    params.log_file =  configFile['Configuration']['log_file_location']
    params.streamer_no_port = params.streamer[:string.find(params.streamer, ":")]
    params.ingest_type = int(configFile['Configuration']['ingest_type'])
    params.create_checksum = configFile['Configuration']['create_checksum']
    params.auto = int(configFile['Configuration']['auto'])
    params.no_delay_assets = int(configFile['Configuration']['no_delay_assets'])
    params.ftp_base_directory = configFile['Configuration']['ftp_base_directory']
    params.blades_ftp_file_location = configFile['Configuration']['blades_ftp_file_location']
    params.ext_id = int(configFile['Configuration']['ext_id'])
    params.playout_profile = str(configFile['Configuration']['playout_profile'])
   
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def print_open_details():
    global params
    if params.streamer == '' :
        log.info("=" * 60 + "\n" + " " * 43 + "Configuration details :\n" + " " * 43 + "   Manager is  : %s .\n" % (params.manager) + " " * 43 + "   Total Number of ingests to reach : %d .\n" % (params.max_sessions) + " " * 43 + "   Number of concurrent ingests : %d .\n" %(params.concurrent_ingests) + " " * 43 + "=" * 60 )
    else :
        log.info("=" * 60 + "\n" + " " * 43 + "Configuration details :\n" + " " * 43 + "   Manager is  : %s .\n" % (params.manager) + " " * 43 + "   Streamer is : %s .\n" % (params.streamer) + " " * 43 + "   Total Number of ingests to reach : %d .\n" % (params.max_sessions) + " " * 43 + "   Number of concurrent ingests : %d .\n" %(params.concurrent_ingests) + " " * 43 + "=" * 60 )   

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def print_end_details():
    global params
   
    log.info("=!" * 30 + "\n" + " " * 43 + "Total successfull ingests allocation to the system =  %d\n" % (params.success_ingests) + " " * 43 + "Total failed ingests allocation to the system =  %d\n" % (params.failed_ingests) + " " * 43 + "end of script\n" + " " * 43 + "=!" * 30)
   

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def stb_ip_parse(ip):
    
    ipNums = ip.split('.')
    ipNums[0] = int(ipNums[0]) 
    ipNums[1] = int(ipNums[1])
    ipNums[2] = int(ipNums[2])
    ipNums[3] = int(ipNums[3])
        
    return ipNums
 
 #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
       
def str_stb_ip_parse(self, ip):
    
    ip[0] = str(ip[0]) 
    ip[1] = str(ip[1])
    ip[2] = str(ip[2])
    ip[3] = str(ip[3])
        
    #ipNums[0] = str(ipNums[0]) 
    #ipNums[1] = str(ipNums[1])
    #ipNums[2] = str(ipNums[2])
    #ipNums[3] = str(ipNums[3])
        
    new_ip = '.'.join(ip)
        
    return new_ip







# Editing the XML for the Streamer load
def addByxPath(dom, xpath):              
    list = dom.xpathEval(xpath)
    for url in list:
        o = url.content
       
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
        ingest_counter = int(url.content)
        #if int(r) == 1:
        #    ingest_counter += 1
       
    return ingest_counter 

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
        if  dom:
            dom.freeDoc()

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def check_existing_ingests(url_num_of_ingests, Ingest_Counter):
    
    global num_of_edges_as_ingest_points
    global version_num
    parse_Ingests_Num = None
       
    try:
        try:
            #print "check existing ingests -->" + str(params.url_num_ingests)
            Ingests_Num_result = urllib2.urlopen(params.url_num_ingests)
            xml_Ingests_Num = Ingests_Num_result.read()
            parse_Ingests_Num = libxml2.parseDoc(xml_Ingests_Num)
            #print parse_Ingests_Num
            if params.streamer == '':
                if version_num[0] > 2:
                    Ingests_Num = int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "//X/num_in_state/elem[9]"))
                else:
                    Ingests_Num = int(checkStrByxPath(Ingest_Counter, parse_Ingests_Num, "//X/num_in_state/elem[17]"))
                if Ingests_Num > 0:
                    Ingests_Num = Ingests_Num / num_of_edges_as_ingest_points
            else:
                Ingests_Num = int(checkByxPath(parse_Ingests_Num, "//X/size"))            
            log.info("=" * 60 + "\n" + " " * 43 + "Existing Concurrent ingests = %d\n" % (Ingests_Num) + " " * 43 + "=" * 60 )
    
           
        except:
            Ingests_Num = params.concurrent_ingests
            log.error("=" * 60 + "\n" + " " * 43 + "Can not retrieve the number of concurrent ingests.\n" + " " *43 + "Manager did not respond .\n" + " " *43 + "Assuming Concurrent ingests = %d\n" % (Ingests_Num) + " " *43 + "=" * 60  )
            time.sleep(10)
            pass
    finally:
        if parse_Ingests_Num:
            parse_Ingests_Num.freeDoc()
   
  #  log.info("=" * 60) + "\n" + " " *43 )
      #  log.info("Can not retrieve the number of concurrent ingests.\n" + " " *43 + "Manager did not respond .")
      #  log.info("Existing Concurrent ingests = %s" % (Ingests_Num))
      #  log.info("=" * 60)

    return Ingests_Num

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



def createAbrAssetXML(id,filename,name,duration,encryption,push,align_gops,streamer_id,initiator,
                      create_checksum,abr,abr_files,is_directory,playout_profile):
    meta = lb.E.meta(lb.E.name(name),lb.E.duration(str(duration)),lb.E.encryption(str(encryption)))

    xml = lb.E.X(
        lb.E.id(str(id)),
        lb.E.filename(filename),
        meta,
        lb.E.push(str(push)),
        lb.E.align_gops(str(align_gops)),
        lb.E.streamer_id(str(streamer_id)),
        lb.E.initiator(initiator),
        lb.E.create_checksum(str(create_checksum)),
        lb.E.abr(str(abr)),
        lb.E.abr_files(lb.E.size(str(1)),lb.E.elem(abr_files,id="0")),
        lb.E.is_directory(str(is_directory)),
        lb.E.playout_profile(str(playout_profile))
         )
    return etree.tostring(xml, pretty_print=True)



def createAsset(index, assetPath, nameStart, nameEnd):
    # initializing the url responses for the exceptions
    global params
    double_slash_index = string.find(assetPath,"//")
    colon_index = string.find(assetPath,":", double_slash_index)
    ftp_user = assetPath[double_slash_index + 2 : colon_index]
    ftp_pass = assetPath[colon_index + 1 :string.find(assetPath,"@",colon_index)]
    strudrl_index = string.find(assetPath,"@",colon_index)
    ftp_ip = assetPath[strudrl_index + 1 :string.find(assetPath,"/",strudrl_index)]
    ftp_ip_index = string.find(assetPath,"/",strudrl_index)
    file_name = assetPath[ftp_ip_index +1:]
    file_name_prefix =  file_name[:string.find(file_name,".")]
    file_name_prefix_index = string.find(file_name,".")
    file_name_sufix =file_name[file_name_prefix_index:]
    asset_preffix_name=nameStart
    asset_suffix_name=nameEnd
    if params.ingest_type != 3:
        assetPath = urllib.quote_plus(assetPath.strip())
        nameStart = urllib.quote_plus(str(nameStart))
        nameEnd = urllib.quote_plus(str(nameEnd))
    d = urllib.quote_plus(str(int(time.time()*1000)))
    dom = None
    # Checking ingest type : regular=1 or ISA/EventIS=2
    if params.ingest_type == 1 :
        if params.create_checksum == 'n' :
            if params.ext_id == 0:
                url = "http://%s/create_asset?id=%s&filename=%s&name=%s_%s%s&duration=-1&encryption=0&type=0&push=0" % (params.manager, d, assetPath, nameStart, index, nameEnd)
            if params.ext_id == 1:
                url = "http://%s/create_asset?id=%s%s_%s%s&filename=%s&name=%s_%s%s&duration=-1&encryption=0&type=0&push=0" % (params.manager, urllib.quote_plus(str(params.blades_ftp_file_location)),str(nameStart),index,nameEnd, assetPath, nameStart, index, nameEnd)
            if params.ext_id == 2:
                url = "http://%s/create_asset?id=%s&filename=%s&name=%s_%s%s&duration=-1&encryption=0&type=0&push=0" % (params.manager, urllib.quote_plus(str(d + "::" + d)), assetPath, nameStart, index, nameEnd)
        else : #(create_checksum = true)
            if params.ext_id == 0:
                url = "http://%s/create_asset?id=%s&filename=%s&name=%s_%s%s&duration=-1&encryption=0&type=0&push=0&create_checksum=1" % (params.manager, d, assetPath, nameStart, index, nameEnd)
            if params.ext_id == 1:
                url = "http://%s/create_asset?id=%s%s_%s%s&filename=%s&name=%s_%s%s&duration=-1&encryption=0&type=0&push=0&create_checksum=1" % (params.manager, urllib.quote_plus(str(params.blades_ftp_file_location)),str(nameStart),index,nameEnd,assetPath, nameStart, index, nameEnd)
            if params.ext_id == 2:
                #url = "http://%s/create_asset?id=%s&filename=%s&name=%s_%s%s&duration=-1&encryption=0&type=0&push=0&create_checksum=1" % (params.manager, urllib.quote_plus(str(d + "::" + d)), assetPath, nameStart, index, nameEnd)
                url = "http://%s/create_asset?id=%s&filename=%s&name=%s_%s%s&duration=-1&encryption=0&type=0&push=0&create_checksum=1" % (params.manager, urllib.quote_plus(str("CNN" + "::" + d)), assetPath, nameStart, index, nameEnd)
        try:        
            try:
        
                response = urllib2.urlopen(url)
               
                xml = response.read()
                dom = libxml2.parseDoc(xml)
                result = addByxPath(dom, "//X/code")
               
                if result == "0":
                    log.info("=" * 60 + "\n" + " " * 43 + "Create ingest number : %d\n" % (index) + " " * 43 + "Asset name : %s_%d%s\n" % (nameStart, index, nameEnd ) + " " * 43 + "=" * 60 )                   
                    #get_streamer_load(params.streamer)
                    params.success_ingests += 1
                   
                else:
                    result = addByxPath(dom, "//X/description")
                    log.error("*" * 60 + "\n" + " " * 43 + "Failed to create ingest number : %d\n" % (index) + " " * 43 + "Error reason: %s\n" % (result) + " " * 43 + "*" * 60 )
                    params.failed_ingests += 1           
            except urllib2.URLError, err:
                log.critical ("*" * 60 + "\n" + " " * 43 + "Failed to create ingest number : %d\n" % (index) + " " * 43 + "Manager error : %s\n" % (err.reason) + " " * 43 + "*" * 60 + "\n" )
                params.failed_ingests += 1        
        finally:
            if dom:
                dom.freeDoc()
    
    elif (params.ingest_type == 2) :
        id = int(time.time()*1000)
        
        ###### create XML message########
           
        msg = '<?xml version="1.0" encoding="US-ASCII" ?>'
        msg += '<!DOCTYPE Message SYSTEM "http://10.204.1.9/DTD/fileservice.dtd">'
        msg += '<Message transactionId="10">'
        msg += '<NetworkTransferRequest transferDirection="import" ip="%s" port="21" userAccount="%s" userPass="%s">' % (str(ftp_ip),str(ftp_user),str(ftp_pass))
        #msg += '<NetworkTransferFile sourcePath="%s%s" targetPath="/dir_/%s__%s%s" transferFormat="binary" startNext="true" size="0"/>' % (params.ftp_base_directory,file_name,str(file_name_prefix),str(index),str(file_name_sufix))
        #msg += '<NetworkTransferFile sourcePath="%s%s" targetPath="/%s__%s%s" transferFormat="binary" startNext="true" size="0"/>' % (params.ftp_base_directory,file_name,str(file_name_prefix),str(index),str(file_name_sufix))
        msg += '<NetworkTransferFile sourcePath="%s%s" targetPath="%s%s__%s%s" transferFormat="binary" startNext="true" size="0"/>' % (params.ftp_base_directory,file_name,str(params.blades_ftp_file_location),str(asset_preffix_name),str(index),str(asset_suffix_name))
        msg += '<CallBackLoc ip="10.0.0.225" port="8080"/>'
        msg += '</NetworkTransferRequest>'
        msg += '</Message>'
                
        #print "send xml:\n" + msg
        print_errors=int(1)
        log.critical ("%s\n" % (msg))
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
        s.send("POST /FSI HTTP/1.0\r\n")
        s.send("Content-Type: text/xml\r\n")
        s.send("Content-Length: "+str(length)+"\r\n\r\n")
    
        try : 
            s.sendall(msg)
            time_after_send_msg = time.time()
            msg_send_time = time_after_send_msg - initial_time
            if msg_send_time > print_errors :
              print "Sending msg time :%s - took too long!!\n" % (msg_send_time)
            else:
              print "Sending msg time : %s\n" % (msg_send_time)
              
            datarecv=s.recv(1024)
            print "Reply Received: "+ str(datarecv)
            if (str(datarecv).find("HTTP/1.0 200 OK") != -1):
                params.success_ingests += 1
            else:
                params.failed_ingests += 1
        
        except socket.error,message :
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n MSG was not sent due to the following socket error : %s \n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n " % (str(message))
        
        s.close()
        time_after_closing_socket = time.time()
        close_socket_time = time_after_closing_socket - initial_time
        print "Closing socket time : %s\n" % (close_socket_time)
        
        return
    elif (params.ingest_type == 3):
        str_xml = createAbrAssetXML(generateAssetID(),"","%s_%s%s"%( nameStart, index, nameEnd),-1,0,0,0,0,"nasfx",1,1,assetPath,1,params.playout_profile)
        print str_xml
        req = urllib2.Request('http://%s/create_asset'%(params.manager))
        req.add_header("Content-Type","text/xml")
        response = urllib2.urlopen(req,data=str_xml)

        xml = response.read()
        dom = libxml2.parseDoc(xml)
        result = addByxPath(dom, "//X/code")
        if result == "0":
            log.info("=" * 60 + "\n" + " " * 43 + "Create ingest number : %d\n" % (index) + " " * 43 + "Asset name : %s_%d%s\n" % (nameStart, index, nameEnd ) + " " * 43 + "=" * 60 )
            #get_streamer_load(params.streamer)
            params.success_ingests += 1

        else:
            result = addByxPath(dom, "//X/description")
            log.error("*" * 60 + "\n" + " " * 43 + "Failed to create ingest number : %d\n" % (index) + " " * 43 + "Error reason: %s\n" % (result) + " " * 43 + "*" * 60 )
            params.failed_ingests += 1


def generateAssetID():
    return int(round(time.time() * 1000))

def checkNumIngestPoints(url):
    global edges_as_ingest_point
    global params
    global version_num
    counter = 0
    edge_is_ingest_point_parse = None
    if ((version_num[0] == 2) and (version_num[1] == 8) and (version_num[3] >= 4)) or (version_num[0] > 2):
        try:
            try:
                edge_is_ingest_point_url = "http://%s/vs_group/get_groups?X=0" % (str(params.manager))
                edge_is_ingest_point_open_url=urllib2.urlopen(edge_is_ingest_point_url)
                edge_is_ingest_point_response = edge_is_ingest_point_open_url.read()
                edge_is_ingest_point_parse = libxml2.parseDoc(edge_is_ingest_point_response)
                list = edge_is_ingest_point_parse.xpathEval("*//props")
                counter = 0
                for i in list:
                    try:
                        if int(i.xpathEval('ingest')[0].content) == 1:
                            if i.xpathEval('replication') != []:
                                counter += int(i.xpathEval('replication')[0].content)
                            else:
                                counter += 1
                    except:
                        pass
                #print counter
                return counter
            except urllib2.URLError, err:
                log.critical ("*" * 60 + "\n" + " " * 43 + "Failed to check num of ingest points " + " " * 43 + "Manager error : %s\n" % (err.reason) + " " * 43 + "*" * 60 + "\n" )
        finally:
            if edge_is_ingest_point_parse:
                edge_is_ingest_point_parse.freeDoc()
        
    else:    
        try:
            try:
                list = url.xpathEval("//X/online/regions/elem/edges/elem/id")
                for i in list:
                    edge_id = i.content
                    edge_is_ingest_point_url = "http://%s/get_edge_props?X=%s" % (params.manager,edge_id)
                    edge_is_ingest_point_open_url=urllib2.urlopen(edge_is_ingest_point_url)
                    edge_is_ingest_point_response = edge_is_ingest_point_open_url.read()
                    edge_is_ingest_point_parse = libxml2.parseDoc(edge_is_ingest_point_response)
                    is_edge_ingest = addByxPath(edge_is_ingest_point_parse, "//X/props/ingest_point")
                    if int(is_edge_ingest) == 1:
                        counter += 1 
                        
                return counter
            
            except urllib2.URLError, err:
                log.critical ("*" * 60 + "\n" + " " * 43 + "Failed to check num of ingest points " + " " * 43 + "Manager error : %s\n" % (err.reason) + " " * 43 + "*" * 60 + "\n" )
        finally:
            if edge_is_ingest_point_parse:
                edge_is_ingest_point_parse.freeDoc()
        
   
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def main():
   
    #Setting default timeout
    socket.setdefaulttimeout(30)
    
    global params   
    global num_of_edges
    global num_of_edges_as_ingest_points
    global version_num
    
    assets_file = open(path+"/"+params.assets_file,"r")
    all_lines = assets_file.readlines()
    num_lines = len(all_lines) - 1  #Number of lines per file
    manager_parse_ver = None
    parse_region = None
    parse_edge = None
    # Getting the Manager version
    try:
        try :
            manager_ver_url = "http://%s/get_versions?X=0" % (params.manager)
            manager_ver_open_url=urllib2.urlopen(manager_ver_url)
            manager_ver_response = manager_ver_open_url.read()
            manager_parse_ver = libxml2.parseDoc(manager_ver_response)
            manager_ver = addByxPath(manager_parse_ver, "//X/mngr_ver")
            CM_ver = addByxPath(manager_parse_ver, "//X/cm_ver")
            print "manager version -->" + str(manager_ver)
        except :
            log.critical("=!" * 30 + "\n" + " " * 43 + "Manager doesn't respond ...\n" + " " * 43 + "Script exit\n" + " " * 43 + "=!" * 30 ) 
            sys.exit()
        
    finally:
        if manager_parse_ver:
            manager_parse_ver.freeDoc()
            
            
    version_num = stb_ip_parse(manager_ver)
    
    
    Ingest_Counter = 0
   
    print_open_details()
   
    #Checking Region ID to receive concurrent ingests
    try:
        try:
                Region_ID_url = "http://%s/get_topology?X=0" % (params.manager)
                Region_result = urllib2.urlopen(Region_ID_url)
                xml_Region = Region_result.read()
                parse_region = libxml2.parseDoc(xml_Region)
                if manager_ver == '2.0.0.1':
                    Region_ID = checkByxPath(parse_region, "//X/online/elem/base/id")
    
                elif ((version_num[0] == 2) and (version_num[1] == 0) and (version_num[3] > 12)) or (version_num[1] == 5) or (version_num[1] == 6) or (version_num[1] >= 7) or (version_num[0] >= 2) :     
                    Region_ID = checkByxPath(parse_region, "//X/online/regions/elem/id")
                else:
                    Region_ID = checkByxPath(parse_region, "//X/online/elem/id")
                
                num_of_edges = checkByxPath(parse_region, "//X/online/regions/elem/edges/size")
                
                num_of_edges_as_ingest_points =  checkNumIngestPoints(parse_region)
                               
                print "Region ID = " + str(Region_ID)
           
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
                #print parse_edge
                if manager_ver == '2.0.0.1':
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
             
             
    line_index = 0
    Real_index = 1
   
    # Setting the url to check the concurrent ingest according to the streamer configuration
    if params.streamer == '':
        #params.url_num_ingests = "http://%s/get_session_state?id=0&reg_id=%s&edge_id=%s&first=0&last=-1 " % (params.manager, Region_ID, Edge_ID)
        params.url_num_ingests = "http://%s/get_session_state?id=0&reg_id=%s&edge_id=0&first=0&last=-1 " % (params.manager, Region_ID)

       
    else :
        params.url_num_ingests = "http://%s:5555/command/monitor_service?id=INGESTION_SESSIONS_IDS&opaque=" % (params.streamer)
   
    # Loop that will add more session in the end...
    while True:

    # Loop that will run on all ingests
        while Real_index <=  params.max_sessions:
           
            # checking for already existing sessions in streamer
            asset_accomulate = 0
            existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)
            while (existing_ingests < params.concurrent_ingests) and (existing_ingests < params.max_sessions) and ((Real_index - 1) < params.max_sessions) :
                
                if line_index > num_lines:
                    line_index = 0
                   
                #for line in all_lines:   # Loop to run on each line in the asset.list file
                line = all_lines[line_index].strip() 
                start_name = line[string.rfind(line, "/")+1:string.rfind(line, ".")].strip()
                end_name = line[string.rfind(line, "."):].strip()
                
                
                
                createAsset(Real_index,line, start_name, end_name)
                if (params.is_delay == "y"):
                    asset_accomulate += 1
                
                if (params.is_delay == "y") and (asset_accomulate == params.no_delay_assets):
                    time.sleep(params.sec_delay)
                    asset_accomulate = 0
                    
                params.ingest_concurrent_counter += 1
                line_index += 1
                Real_index += 1
               
                time.sleep(0.05)
                existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)
                                
            log.info("=" * 60 + "\n" + " " * 43 + "Total successful ingests so far = %d\n" % (params.success_ingests) + " " * 43 + "=" * 60)
             
            time.sleep(5)   

        if (params.auto == 1):
            existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)
            while (existing_ingests > 0):
                existing_ingests = check_existing_ingests(params.url_num_ingests, Ingest_Counter)
                time.sleep(5)
            break

        else:
            pass
        
        ans = string.lower(raw_input("\nWould you like to add more sessions? \n"))
        
           
        while (ans != 'y') and (ans != 'n'):
            ans = string.lower(raw_input("Wrong Input!!!\nWould you like to add more sessions? (y/n): \n"))
                 
        if ans == 'y':
            sess_tmp = int(raw_input("How many sessions?\n "))
            params.max_sessions += sess_tmp
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
    version_num = []
    num_of_edges = 0
    num_of_edges_as_ingest_points = 0
    main()
   

