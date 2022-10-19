#import sys
#import string
import time
import urllib2
import urllib
import libxml2
#import logging
from configobj import ConfigObj #to read config file
#import signal
import os #os function file manipulation
from pexpect import pxssh 
import requests

def delete_recording(manager,dom, xpath,num_recording):    
    num_of_delete = 0  
    print manager, xpath,num_recording     
    list = dom.xpathEval(xpath)
    if num_recording == 0:
        for node in list:
            #print "node = " + str(node)
            url="http://%s/remove_rsdvr_session?id=%s" % (manager, urllib.quote_plus(node.content))
            #print "url 2 delete--> %s" % (url)
            actual_delete = send_delete(url,node.content)
            if actual_delete == 1:
                num_of_delete += 1
        return num_of_delete
    else :
        index=1
        #print "index=%s ; num_recording=%s" % (index,num_recording )
        #print "list=%s" %(list)
        for node in list:
            if index <= num_recording :
                url="http://%s/remove_rsdvr_session?id=%s" % (manager, urllib.quote_plus(node.content))
                #print "url 2 delete--> %s" % (url)
                actual_delete = send_delete(url,node.content)
                if actual_delete == 1:
                    num_of_delete += 1
            index += 1
        return num_of_delete

def send_delete(url,node_content):
    #try :
        #response = urllib2.urlopen(url)
        p = 1;
        retry = 30
        while p !=0 and retry>0:
            p = os.system("wget -T1 -o /dev/null \"%s\" 1>/dev/null " % (url))
        #xml = response.read()
        #dom = libxml2.parseDoc(xml)
        #result = checkByxPath(dom, "/X")
        #start_result = result.startswith("Asset could not be deleted")
        #if start_result == False:
            if (p == 0):
                print "Asset : %s was deleted successfully." % (node_content)
                return 1;
            else:
                time.sleep(1)
                print "Retry " +str(retry)
                retry-=1
                
        print "Asset : %s could not be deleted .\n Error from manager ." % (node_content)
        return 0
                #return 0;

    #except urllib2.URLError, err:
        #print "Couldn't open URL for delete .\n url : %s . \n Manager Error : %s ." % (url,err.reason)
  

def checkByxPath(dom, xpath):   
                
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content

    return r





def from_list_to_array():
    global num_of_total_recording
    global manager
    total_recording_array = ()    
    global num_of_delete    
    global remove_all_recordings
    global wait
    actual_delete = 0
    
    if remove_all_recordings == 'y':
        total_remaining = num_of_total_recording
    else :
        total_remaining = num_of_delete
        
        
    offset = 0       
    while ( total_remaining > 0):
        #we set num to get =100 because this is configured in the manager ini file              
        #url = "http://%s/get_all_assets?asset_type=0&offset=%s&num_to_get=100" % (manager,offset)
        if total_remaining >= 100:
            url = "http://%s/get_recordings?max_items=100&offset=%s" % (manager,offset)
        else :
            url = "http://%s/get_recordings?max_items=%s&offset=%s" % (manager,total_remaining,offset)
        #print "url = " + url
        try:
            all_assets = urllib2.urlopen(url,timeout=10)
        except urllib2.HTTPError:
            continue
            
        xml = all_assets.read()
        assets_list = libxml2.parseDoc(xml)
        list__external_id = assets_list.xpathEval("//X/info/elem/recording/external_id")
        
        print ("<<<<<<>>>>>>>>>> total remaining" + str(total_remaining))
        for node in list__external_id:
            total_recording_array = total_recording_array + (node.content.strip(),)
            
        
            
                   
        total_remaining = int(total_remaining) - 100
        offset = int(offset) + 100
        time.sleep(1)
        assets_list.freeDoc()
    for node in total_recording_array:   
            url="http://%s/remove_rsdvr_session?id=%s" % (manager, urllib.quote_plus(node))
            #print "url 2 delete--> %s" % (url)
            #actual_delete = send_delete(url,node.content)
            if wait == 'y':
                response = urllib2.urlopen(url,timeout=10)
                xml = response.read()
                dom = libxml2.parseDoc(xml)
                result = checkByxPath(dom, "/X")
                #print ("<<<<<<>>>>>>>>>>" + str(total_remaining))
                start_result = result.startswith("Asset could not be deleted")
                if start_result == True:
                    print ("Could not delete recording")
                    
                else: 
                    print ("delete recording " + node)
                    actual_delete += 1
                dom.freeDoc() 
            else:
                send_delete(url,node)
                actual_delete += 1
            time.sleep(0.01)
                #total_recording_array = total_recording_array + (node.content.strip(),)
            #if actual_delete == 1:
            #    num_of_delete += 1
        
    #print "<<>> len total array" + str(len(total_recording_array))
    #print "<<<<<<<<<>>>>>>>>>>>>>>>>> " + total_recording_array
    return actual_delete




def del_reasset():
    data_id=[]
    cmd = '''/opt/solidDB/soliddb-6.5/bin/solsql -x onlyresults -e "select external_id from live_recording_session where external_id like 'REASSET''' + '''%' and status='0' and active='1'" 'tcp 2315' fabrix fabrix'''
    print "query: " +  cmd
    s = pxssh.pxssh()
    s.force_password = True
    s.login(db_addr, 'root', db_machine_password)
    s.sendline("clear")
    s.prompt()
    s.sendline(cmd)
    s.prompt()
    output = s.before
#print output
    for line in output.split("\n"):
        if "solsql" not in line.strip() and line.strip() != '':
            data_id.append(line.strip())
 #   print data_id 
#    print "fff"
    for npvr in data_id:
            url="http://%s/remove_rsdvr_session?id=%s" % (manager, urllib.quote_plus(npvr))
            #print "url 2 delete--> %s" % (url)
            #actual_delete = send_delete(url,node.content)

            response = urllib2.urlopen(url,timeout=10)
            xml = response.read()
            dom = libxml2.parseDoc(xml)
            result = checkByxPath(dom, "/X")
            #print ("<<<<<<>>>>>>>>>>" + str(total_remaining))
            start_result = result.startswith("Asset could not be deleted")
            if start_result == True:
                print ("Could not delete recording")
                
            else: 
                print ("delete recording " + npvr)








# ------------------------------------------------------
# Main

# Getting current folder location
path = "../"
#path = os.getcwd()

# Reading configuration file
config = ConfigObj(path+'/conf/config.ini')

manager = config['Configuration']['manager']
remove_all_recordings = config['Configuration']['all_recordings']
num_of_delete = int(config['Configuration']['size_remove_recording'])
wait = config['Configuration']['wait']
reasset = int(config['Configuration']['reasset'])
db_addr = config['Configuration']['db_addr']
db_machine_password = config['Configuration']['db_machine_password']




# Getting the manager version
manager_ver_url = "http://%s/get_versions?X=0" % (manager)
manager_ver_open_url=urllib2.urlopen(manager_ver_url)
manager_ver_response = manager_ver_open_url.read()
manager_parse_ver = libxml2.parseDoc(manager_ver_response)
manager_ver = checkByxPath(manager_parse_ver, "//X/mngr_ver")
manager_parse_ver.freeDoc()
#
#print "manager version -->" + str(manager_ver)

if reasset == 0:
# Opening the XML of the recording list
    url = "http://%s/get_recordings?max_items=10000&offset=0" % (manager)
    #print "url = " + url
    all_recordings = urllib2.urlopen(url)
    xml = all_recordings.read()
    recording_list = libxml2.parseDoc(xml)
    num_of_total_recording = checkByxPath(recording_list , "//X/total_recordings")
    #print "asset-list -->" + str(recording_list)
    print "*****************************\n <<<<<<<<<<<<< Total deleted recordings %d " % from_list_to_array()
    
    
    # Deleting the recordings list
    #if remove_all_recordings == 'y':
     #   print "************************************************************\n <<<<<<<<<<<<< Total deleted recordings %d >>>>>>>>>>>>>>>>>>" % delete_recording(manager, recording_list, "//X/info/elem/recording/external_id", 0)
    #    print "************************************************************"
    #else :
    #    print "************************************************************\n <<<<<<<<<<<<< Total deleted recordings %d >>>>>>>>>>>>>>>>>>" % delete_recording(manager, recording_list, "//X/info/elem/recording/external_id", num_of_delete)
    #   print "************************************************************"
    #time.sleep(1)
    os.system("find %s -name \'remove_rsdvr_ses*\'  | xargs rm" % (path))
    print "\n\nFinished deleting recording list"
    raw_input("press any key to continue")

else:
    del_reasset()
