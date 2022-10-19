#import sys
import string
#import time
import urllib2
import urllib
import libxml2
#import logging
from configobj import ConfigObj #to read config file
#import signal
import os #os function file manipulation
import socket
import xml.sax.saxutils
import traceback
import subprocess
import shlex
import requests
from gtk._gtk import ResponseType

def delete_channels(manager,dom, xpath,num_channels, mgr_version):  
    #print manager, xpath,num_channels     
    list = dom.xpathEval(xpath)
    if num_channels == 0:
        for node in list:
            #print "node = " + str(node)
            if mgr_versions == 0 :
                url="http://%s/multicast_channel/delete?X=%s" % (manager, urllib.quote_plus(node.content))
            elif mgr_versions == 1 :
                url="http://%s/multicast_channel/delete_by_name?X=%s" %( manager, urllib.quote_plus(node.content))
            #print "url 2 delete--> %s" % (url)
            actual_delete = send_delete_channels(url,node.content)
    else :
        index=1
        #print "index=%s ; num_rsdvr=%s" % (index,num_rsdvr )
        #print "list=%s" %(list)
        for node in list:
            if index <= num_channels :
                if mgr_versions == 0 :
                    url="http://%s/multicast_channel/delete?X=%s" % (manager, urllib.quote_plus(node.content))
                elif mgr_versions == 1 :
                    url="http://%s/multicast_channel/delete_by_name?X=%s" %( manager, urllib.quote_plus(node.content))
                #print "url 2 delete--> %s" % (url)
                actual_delete = send_delete_channels(url,node.content)
            index += 1


def send_delete_channels(url,node_content):
    global counter_delete_channel
    global total_boxes_size
    dom =None
    try:
        try :
            response = urllib2.urlopen(url)
            xml = response.read()
            dom = libxml2.parseDoc(xml)
            result = checkByxPath(dom, "/X/return_code")
            if result == "0":
                #print "Channel : %s was deleted successfully." % (node_content)
                counter_delete_channel += 1
            else:
                print "Channel : %s could not be deleted .\n Error from manager : %s ." % (node_content, result)
    
        except urllib2.URLError, err:
            print "Couldn't open URL for delete .\n url : %s . \n Manager Error : %s ." % (url,err.reason)
    finally:
        if dom:
            dom.freeDoc()
  
def delete_home_id(manager,dom, xpath, num_home_id, start_del_box_id):  
    #print manager, xpath,num_home_id, start_del_box_id
    global total_offset     
    list = dom.xpathEval(xpath)
    home_id_list=None
    if num_home_id == 0: 
        for node in list:
            if (node.content != 'NPVR') and (node.content != 'Pause') : 
                #print "node = " + str(node)
                msg = '<?xml version="1.0" encoding="utf-8"?><DeprovisionHome HomeID="%s"/>' % (node.content)
                #print "send xml:\n" + msg
                actual_delete = send_delete_home_id(manager,msg,node.content)
        return
                
    elif num_home_id == -1:
        return 
    else :
        
        
        for node in list:
            if (node.content != 'NPVR') and (node.content != 'Pause') and (int(node.content) == start_del_box_id)  :                
                if num_home_id <= 100:
                    index = 0
                    url = "http://%s/get_boxes?offset=%s&limit=100" % (manager,str(total_offset))
                    print "url = " + url
                    all_home_id = urllib2.urlopen(url)
                    xml = all_home_id.read()
                    #home_id_list.freeDoc()
                    home_id_list = libxml2.parseDoc(xml)                   
                    list = home_id_list.xpathEval("//X/boxes/elem/external_id")
                    for node in list:
                        if index < num_home_id:
                            msg = '<?xml version="1.0" encoding="utf-8"?><DeprovisionHome HomeID="%s"/>' % (node.content)
                            send_delete_home_id(manager,msg,node.content)
                            index += 1
                        else:
                            home_id_list.freeDoc()
                            return 1
                    home_id_list.freeDoc()                    
                else:
                    index = 0
                    for i in range (1 ,(total_boxes_size / 100) + 2) :
                        url = "http://%s/get_boxes?offset=%s&limit=100" % (manager,str(total_offset))
                        print "url = %s" % str(url)
                        all_home_id = urllib2.urlopen(url)
                        xml = all_home_id.read()
                        home_id_list = libxml2.parseDoc(xml)
                        list = home_id_list.xpathEval("//X/boxes/elem/external_id")
                        for node in list:
                            if index < num_home_id:
                                msg = '<?xml version="1.0" encoding="utf-8"?><DeprovisionHome HomeID="%s"/>' % (node.content)
                                send_delete_home_id(manager,msg,node.content)
                                index += 1
                            else:
                                home_id_list.freeDoc()
                                return 1                    
                        home_id_list.freeDoc()
            total_offset += 1
#        home_id_list.freeDoc()     
        return 0        
          
def delete_home_id_by_db(manager, num_home_id, start_del_box_id):
         global db_addr, db_machine_password
         path = "../"         
         if num_home_id != 0 and start_del_box_id !=0:
             if db_type == "solid" :
                 x = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \'select id from rsdvr_box where active='1' and EXTERNAL_ID='%s'' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows > tmp.db  '''  % (str(db_addr),str(start_del_box_id),str(db_machine_password))
                 try:
                    print x
                    os.system(x)
                 except:
                     traceback.print_exc(file=sys.stdout)
             else:
                x = '''expect -c "set timeout -1;
                spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \' select id from rsdvr_box where active='1' and EXTERNAL_ID='%s'';sleep 1 \); done; exit;\\";
                match_max 100000;
                expect *password:*;
                send -- %s\\r;
                interact;" | tr -d ' ' | sed '/^\s*$/d' | grep -v "spawn\|sess\|passwo\|---\|rows"  > tmp.db'''  % (str(db_addr),str(db_addr),str(start_del_box_id),str(db_machine_password))
                print x
                try:
                    os.system(x)
                except:
                    traceback.print_exc(file=sys.stdout)         
                
                
             parameters_file = open("tmp.db","a")
             parameters_file.close()
             parameters_file = open("tmp.db","r")
             internal_initial_box_num = str(parameters_file.readline()).strip()
             parameters_file = open("tmp.db","w")
             parameters_file.write('')
             parameters_file.close()
             if internal_initial_box_num == '':
                 print "Could not find initial_box_Num - exiting!!!!"
                 exit()
             else:
                pass             
             print "internal_initial_box_num = %s \n" % (internal_initial_box_num)
             if db_type == "solid" :
                 x  = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \\\\\\"select external_id from rsdvr_box where active=1 and id>= \(select id from rsdvr_box where active=1 and external_id=%s\) and external_id<>'NPVR' order by id limit %s\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows   > tmp.db'''  % (str(db_addr),str(start_del_box_id),str(num_home_id),str(db_machine_password))
                 try:
                    print x
                    result = subprocess.check_output(x, shell=True)                            
                 except:
                    traceback.print_exc(file=sys.stdout)
             else:
                 x = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \\\\\\" select external_id from rsdvr_box where active=1 and id>= \(select id from rsdvr_box where active=1 and external_id='%s'\) and external_id<>'NPVR' order by id limit %s\\\\\\";sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | tr -d ' ' | sed '/^\s*$/d' | grep -v "spawn\|sess\|passwo\|---\|rows"  > tmp.db'''  % (str(db_addr),str(db_addr),str(start_del_box_id),str(num_home_id),str(db_machine_password))
                 print x
                 try:
                     os.system(x)
                 except:
                     traceback.print_exc(file=sys.stdout)         
                 
                 
             lines = open('tmp.db',"r").readlines()
             count = 0
             for line in lines:
                 if count < int(num_home_id):
                     msg = '<?xml version="1.0" encoding="utf-8"?><DeprovisionHome HomeID="%s"/>' % (line.strip())
                     send_delete_home_id(manager,msg,line.strip())
         else:
             limit_for_delete_all=500000
             if db_type == "solid" :
                 x  = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \\\\\\"select external_id from rsdvr_box where active=1 and external_id<>'NPVR' order by id limit %s\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows   > tmp.db'''  % (str(db_addr),str(limit_for_delete_all),str(db_machine_password))
                 try:
                    print x
                    result = subprocess.check_output(x, shell=True)                            
                 except:
                    traceback.print_exc(file=sys.stdout)
             else:
                 x = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"export PGPASSWORD=fabrix ;for i in $\(seq 1 1\); do \(psql -t -U fabrix -d manager -h %s -p 9999 -c \\\\\\" select external_id from rsdvr_box where active=1 and external_id<>'NPVR' order by id limit %s\\\\\\";sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | tr -d ' ' | sed '/^\s*$/d' | grep -v "spawn\|sess\|passwo\|---\|rows"  > tmp.db'''  % (str(db_addr),str(db_addr),str(limit_for_delete_all),str(db_machine_password))
                 print x
                 try:
                    print x
                    result = subprocess.check_output(x, shell=True)                            
                 except:
                    traceback.print_exc(file=sys.stdout)
                 
                 
             lines = open('tmp.db',"r").readlines()
             count = 0
             for line in lines:
                 if count < int(num_home_id):
                     msg = '<?xml version="1.0" encoding="utf-8"?><DeprovisionHome HomeID="%s"/>' % (line.strip())
                     send_delete_home_id(manager,msg,line.strip())
                     print "Deleted Box: %s" %  (line.strip())                   
         x = '''rm -f tmp.db'''
         try:
             print x
             result = subprocess.check_output(x, shell=True)                            
         except:
             traceback.print_exc(file=sys.stdout)






def delete_home_id_by_proxy_db(manager, num_home_id, start_del_box_id):
         global db_addr, db_machine_password
         path = "../"         
         if num_home_id != 0 and start_del_box_id !=0:
             x = '''expect -c "set timeout -1;
             spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \'select id from mp_rsdvr_box where ID='%s'' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
             match_max 100000;
             expect *password:*;
             send -- %s\\r;
             interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows > tmp.db  '''  % (str(db_addr),str(start_del_box_id),str(db_machine_password))
             try:
                print x
                os.system(x)
             except:
                 traceback.print_exc(file=sys.stdout)
             parameters_file = open("tmp.db","a")
             parameters_file.close()
             parameters_file = open("tmp.db","r")
             internal_initial_box_num = str(parameters_file.readline()).strip()
             parameters_file = open("tmp.db","w")
             parameters_file.write('')
             parameters_file.close()
             if internal_initial_box_num == '':
                 print "Could not find initial_box_Num - exiting!!!!"
                 exit()
             else:
                pass 
             print "internal_initial_box_num = %s \n" % (internal_initial_box_num)
             x  = '''expect -c "set timeout -1;
             spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \'select id from mp_rsdvr_box where cast (id as int)>=%s order by cast(id as int) limit %s' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
             match_max 100000;
             expect *password:*;
             send -- %s\\r;
             interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows  > tmp.db'''  % (str(db_addr),str(start_del_box_id),str(num_home_id),str(db_machine_password))
             try:
                print x
                result = subprocess.check_output(x, shell=True)                            
             except:
                traceback.print_exc(file=sys.stdout)
             lines = open('tmp.db',"r").readlines()
             count = 0
             for line in lines:
                 if count < int(num_home_id):
                     msg = '<?xml version="1.0" encoding="utf-8"?><DeprovisionHome HomeID="%s"/>' % (line.strip())
                     send_delete_home_id(manager,msg,line.strip())
         else:
             limit_for_delete_all=500000
             x  = '''expect -c "set timeout -1;
             spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \'select id from mp_rsdvr_box  order by cast(id as int) limit %s' \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
             match_max 100000;
             expect *password:*;
             send -- %s\\r;
             interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows   > tmp.db'''  % (str(db_addr),str(limit_for_delete_all),str(db_machine_password))
             try:
                print x
                result = subprocess.check_output(x, shell=True)                            
             except:
                traceback.print_exc(file=sys.stdout)
             lines = open('tmp.db',"r").readlines()
             count = 0
             for line in lines:
                 if count < int(num_home_id):
                     msg = '<?xml version="1.0" encoding="utf-8"?><DeprovisionHome HomeID="%s"/>' % (line.strip())
                     send_delete_home_id(manager,msg,line.strip())                         
         x = '''rm -f tmp.db'''
         try:
             print x
             result = subprocess.check_output(x, shell=True)                            
         except:
             traceback.print_exc(file=sys.stdout)




















                
                
def send_delete_home_id(manager,msg,node_content):
    global counter_delete_home_id,is_rsdvr_rev3
    
    if is_rsdvr_rev3 != 2:
        try :
            print "*****\nbox to delete --> %s\n*****" %(node_content)
            length=len(msg)
            manager_ip = manager[:string.find(manager, ":")]
            manager_port = int(manager[string.find(manager, ":")+1:])
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((manager_ip, manager_port))
            s.send("POST /%s HTTP/1.0\r\n" % (rsdvr_rev))
            s.send("Content-Type: text/xml\r\n")
            s.send("Content-Length: "+str(length)+"\r\n\r\n")
            s.send(msg)
            datarecv=s.recv(1024)
            print "Reply Received: "+ str(datarecv)
            s.close()
            counter_delete_home_id += 1
        except urllib2.URLError, err:
            print "Couldn't open URL for delete .\n url : %s . \n Manager Error : %s ." % (str(datarecv),err.reason)
    else: #v2
#        xml = """<ProvisionHome HomeID="%s" GeoID="%s" Quota="%s" QuotaType="2" Type="2" />""" % (str(home_id),str(boxes_by_sg[count]), str(box_size))
#        headers = {'Content-Type' : 'text/x-xml2'}
        res = requests.delete('http://' + str(manager) + '/v2/homes/' + node_content)
        print(res.text)



def checkByxPath(dom, xpath):   
                
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content

    return r

def stb_ip_parse(ip):
    
    ipNums = ip.split('.')
    ipNums[0] = int(ipNums[0]) 
    ipNums[1] = int(ipNums[1])
    ipNums[2] = int(ipNums[2])
    ipNums[3] = int(ipNums[3])
        
    return ipNums


def check_if_manager_proxy():
    global is_proxy
    global managers
    global regions
    global manager  
    url = "http://%s/fxhelp" % (manager)
    manager_fxhelp_open_url=urllib2.urlopen(url)
    manager_fxhelp_response = manager_fxhelp_open_url.read()
    #manager_parse_fxhelp = libxml2.parseDoc(manager_fxhelp_response)
    if (str(manager_fxhelp_response).find("Manager Proxy") != -1):
        is_proxy = 1
        url = "http://%s/get_regions?X=0" % str(manager)
        regions_open_url=urllib2.urlopen(url)
        regions_response = regions_open_url.read()
        regions_parse = libxml2.parseDoc(regions_response)
        list = regions_parse.xpathEval("//X/regs/elem/id")
        #list = xpathEval(regions_parse, "//X/regs/elem/id")
        for url in list:
            regions.append(url.content)
        list = regions_parse.xpathEval("//X/regs/elem/manager_addr")
        for url in list:
            managers.append(url.content)
    else:
        is_proxy = 0

# ------------------------------------------------------
# Main

# Getting current folder location
path = "../"
#path = os.getcwd()

# Reading configuration file
config = ConfigObj(path+'/conf/config.ini')

manager = config['Configuration']['manager']
remove_all_rsdvr = config['Configuration']['all_rsdvr']
num_of_delete = int(config['Configuration']['size_delete_rsdvr'])
start_del_box_id = int(config['Configuration']['start_del_box_id'])
remove_channels = config['Configuration']['delete_channels']
num_of_delete_channels = int(config['Configuration']['size_delete_channels'])
is_rsdvr_rev3 = int(str(config['Configuration']['is_rsdvr_rev3']).strip())
sg_to_del = str(config['Configuration']['sg_to_del']).strip()
db_addr = config['Configuration']['db_addr']
use_db = int(str(config['Configuration']['use_db']).strip())
db_machine_password = str(config['Configuration']['db_machine_password']).strip()
db_type = str(config['Configuration']['db_type']).strip()

# if this manager proxy
is_proxy = 0
regions = []
managers = []
########################

if is_rsdvr_rev3==0:
    rsdvr_rev='RSDVR'
elif is_rsdvr_rev3==1:
    rsdvr_rev='Rev3_RSDVR'
else:
    print ' ---------------------------------- invalid RSDVR revision -----------------------------------'

check_if_manager_proxy()

# Getting the manager version
manager_ver_url = "http://%s/get_versions?X=0" % (manager)
manager_ver_open_url=urllib2.urlopen(manager_ver_url)
manager_ver_response = manager_ver_open_url.read()
manager_parse_ver = libxml2.parseDoc(manager_ver_response)
manager_ver = checkByxPath(manager_parse_ver, "//X/mngr_ver")
manager_parse_ver.freeDoc()
total_offset = 0
version_num = stb_ip_parse(manager_ver)

#print "manager version -->" + str(manager_ver)
counter_delete_home_id = 0
counter_delete_channel = 0

# Opening the XML of the channels list
if (version_num[0] == 2) and (version_num[1] == 6) and (version_num[3] >= 4) or (version_num[1] >= 7) or (version_num[0] >= 3):
    if (is_rsdvr_rev3 == 0 or is_rsdvr_rev3 == 2):
        url = "http://%s/multicast_channel/get_all?offset=0&limit=10000" % (manager)
    else:
        url = "http://%s/Rev3_RSDVR?type=GetChannelMapData" % (str(manager))
else :
    url = "http://%s/multicast_channel/get_all?X=0" % (manager)
if (is_proxy == 0 and is_rsdvr_rev3 != 2):
    print "url = " + url
    all_channels = urllib2.urlopen(url)
    xml = all_channels.read()
    channels_list = libxml2.parseDoc(xml)
    print "channels-list -->" + str(channels_list)


if is_proxy == 0:
    # Opening the XML of the home_id's list
    url = "http://%s/get_boxes?offset=0&limit=100" % (manager)
    #print "url = " + url
    all_home_id = urllib2.urlopen(url)
    xml = all_home_id.read()
    home_id_list = libxml2.parseDoc(xml)
    #print "boxes-list -->" + str(home_id_list)
    
    total_boxes_size = int(checkByxPath(home_id_list ,"//X/total_count"))
    print "Total_number of boxes in the system : %s \n" % (total_boxes_size)

else:
    total_boxes_size = 0
    if (version_num[0] == 2) and (version_num[1] >= 8) and (version_num[2] >= 0) and (version_num[3] >= 4) or (version_num[0] >= 3):
        url = "http://%s/get_boxes?offset=0&limit=100" % (manager)
        #print "url = " + url
        all_home_id = urllib2.urlopen(url)
        xml = all_home_id.read()
        home_id_list = libxml2.parseDoc(xml)
        #print "boxes-list -->" + str(home_id_list)
        
        total_boxes_size = int(checkByxPath(home_id_list ,"//X/total_count"))
        print "Total_number of boxes in the system : %s \n" % (total_boxes_size)
        
        
    else:
        for i in range(len(managers)):
            # Opening the XML of the home_id's list
            url = "http://%s/get_boxes?offset=0&limit=100" % (managers[i])
            #print "url = " + url
            try:
                all_home_id = urllib2.urlopen(url, timeout=10)
                xml = all_home_id.read()
                home_id_list = libxml2.parseDoc(xml)
                #print "boxes-list -->" + str(home_id_list)
                total_boxes_size += int(checkByxPath(home_id_list ,"//X/total_count"))
            except urllib2.URLError, e:
                 total_boxes_size +=0
                 print "could not calculate num of boxes of manager %s" % (managers[i]) 
        print "Total_number of boxes in the system : %s \n" % (total_boxes_size)

if is_proxy == 0:
    if use_db == 0:
        box_fetch = 100 
        for i in range (1 ,(total_boxes_size / 100) + 2) :
            #if i == 1 :
            #    current_range = 0
        
        
        
            # Deleting the rsdvr
            if remove_all_rsdvr == 'y':
                delete_home_id(manager,home_id_list, "//X/boxes/elem/external_id", 0 ,0)
                url = "http://%s/get_boxes?offset=0&limit=100" % (manager)
                #print "url = " + url
                all_home_id = urllib2.urlopen(url)
                xml = all_home_id.read()
                home_id_list = libxml2.parseDoc(xml)
                
            else :
                
                url = "http://%s/get_boxes?offset=%s&limit=100" % (manager,total_offset)
                #print "url = " + url
                all_home_id = urllib2.urlopen(url)
                xml = all_home_id.read()
                home_id_list = libxml2.parseDoc(xml)
                
                return_code = delete_home_id(manager,home_id_list, "//X/boxes/elem/external_id", num_of_delete, start_del_box_id)
                if return_code == 1 :
                   break
                else:
                    pass
    else: #delete by db
           if remove_all_rsdvr == 'y':
               delete_home_id_by_db(manager, total_boxes_size ,0)
           else:
               delete_home_id_by_db(manager, num_of_delete, start_del_box_id)     
##this is proxy manager       
else:
## if we delete without the database:    
    if use_db == 0:
        if is_rsdvr_rev3 != 2: 
            url = "http://%s/Rev3_RSDVR?type=GetHomes" % (manager)
            #print "url = " + url
            all_home_id = urllib2.urlopen(url)
            xml = all_home_id.read()
            home_id_list = libxml2.parseDoc(xml)
        elif is_rsdvr_rev3 == 2:
            url = "http://%s/get_boxes?offset=0&limit=1000000" % (manager)
            all_home_id = urllib2.urlopen(url)
            xml = all_home_id.read()
            home_id_list = libxml2.parseDoc(xml)
        if is_rsdvr_rev3==0:
            list = home_id_list.xpathEval("//GetHomesResponse/HomeList/Home")
        elif is_rsdvr_rev3==1:
            list = home_id_list.getRootElement().get_children().get_children()
        elif is_rsdvr_rev3==2:
            list = home_id_list.xpathEval("//X/boxes/elem/box_data/external_id") 
        if remove_all_rsdvr == 'y':
            counter_delete_home_id = 0
            for url in list:
                if is_rsdvr_rev3 != 2:
                    home_id = url.prop("HomeID")
                    sg = url.prop("ID")
                    if (home_id != 'NPVR') and (home_id != 'Pause'):
                        try:       
                            del_url = "http://%s/Rev3_RSDVR?type=DeprovisionHome&HomeID=%s" % (manager,home_id)
                            urllib2.urlopen(del_url)
                            print "Delete Home ID - %s, SG - %s" % (home_id,sg)
                            counter_delete_home_id += 1
                        except:
                            pass
                else:
                    requests.delete('http://' + str(manager) + '/v2/homes/' + url.content)
    # remove from specific box        
        else:
            # if we delete by home ID
            if start_del_box_id >= 0:
                if is_rsdvr_rev3 != 2:      
                    url = "http://%s/Rev3_RSDVR?type=GetHomeProfileDetails&HomeID=%s" % (manager,start_del_box_id)
                elif is_rsdvr_rev3 == 2:
                    url = "http://%s/get_boxes?offset=0&limit=1000000" % (manager)
                start_home_id = urllib2.urlopen(url)
                xml = start_home_id.read()
                start_home_id_xml = libxml2.parseDoc(xml)
                if is_rsdvr_rev3==0:
                    start_home_id_detail = start_home_id_xml.xpathEval("/HomeProfileDetailsResponse")
                elif is_rsdvr_rev3==1:
                    start_home_id_detail = start_home_id_xml.getRootElement()
                elif is_rsdvr_rev3==2:
                    list = home_id_list.xpathEval("//X/boxes/elem/box_data/external_id")
                if is_rsdvr_rev3 !=2 :
                    for url in start_home_id_detail:
                        response = url.prop("ReasonDescription")
                        break
                    if response == "OK" and num_of_delete != -1:  
                        counter_delete_home_id = 0
                        found_box_flag = 0
                        for url in list:
                            home_id = url.prop("HomeID")
                            sg = url.prop("ID")
                            if (home_id != 'NPVR') and (home_id != 'Pause'):
                                if home_id == str(start_del_box_id):
                                    found_box_flag = 1
                                if (found_box_flag == 1) and (counter_delete_home_id < num_of_delete) and (home_id != ''):
                                    try:  
                                        del_url = "http://%s/Rev3_RSDVR?type=DeprovisionHome&HomeID=%s" % (manager,home_id)
                                        urllib2.urlopen(del_url)
                                        print "Delete Home ID - %s, SG - %s" % (home_id,sg)
                                        counter_delete_home_id += 1
                                    except:
                                        pass
                                elif (counter_delete_home_id >= num_of_delete) or (home_id == ''):
                                    break
                elif is_rsdvr_rev3 ==2:
                    if num_of_delete != -1:  
                        counter_delete_home_id = 0
                        found_box_flag = 0
                        for url in list:                                
                            if (url.content != 'NPVR') and (url.content != 'Pause'):
                                if url.content == str(start_del_box_id):
                                    found_box_flag = 1
                                if (found_box_flag == 1) and (counter_delete_home_id < num_of_delete) and (url.content != ''):
                                    try:  
                                        requests.delete('http://' + str(manager) + '/v2/homes/' + url.content)
                                        print "Delete Home ID - %s" % (str(url.content))
                                        counter_delete_home_id += 1
                                    except:
                                        pass
                                elif (counter_delete_home_id >= num_of_delete) or (url.content == ''):
                                    break
                else:
                    print "Start Home ID %s does not exist" % (str(start_del_box_id))                
            # If we delete by service group
            else:
               if is_rsdvr_rev3 != 2: 
                   if num_of_delete > 0:                        
                       actual_sg = []
                       break_flag = 0
                       reqired_sg_to_del_array = map(int, sg_to_del.split(';'))
                       url = "http://%s/Rev3_RSDVR?type=GetServiceGroups" % (manager)
                       sg = urllib2.urlopen(url)
                       xml = sg.read()
                       sg_xml = libxml2.parseDoc(xml)
                       sg_list = sg_xml.xpathEval("//ServiceGroupList/ServiceGroup")
                       for i in reqired_sg_to_del_array:
                           for url in sg_list:
                               sg = url.prop("ID")
                               if  sg == str(i):
                                   actual_sg.append(sg)  
                       #print actual_sg 
                       if actual_sg != []:
                           counter_delete_home_id = 0
                           for url in list:
                                box_sg = url.prop("ServiceGroup")
                                home_id = url.prop("HomeID")
                                for i in actual_sg:
                                    if i == box_sg:
                                        try:
                                            del_url = "http://%s/Rev3_RSDVR?type=DeprovisionHome&HomeID=%s" % (manager,home_id)
                                            urllib2.urlopen(del_url)
                                            print "Delete Home ID - %s , SG - %s" % (home_id,box_sg)
                                        except:
                                            pass
                                        counter_delete_home_id += 1                            
                                        if counter_delete_home_id >= num_of_delete and start_del_box_id != -2:
                                            break_flag = 1
                                            break
                                if (break_flag == 1):
                                    break
               elif is_rsdvr_rev3 == 2:
                   if num_of_delete > 0:                        
                       actual_sg = []
                       break_flag = 0
                       reqired_sg_to_del_array = map(int, sg_to_del.split(';'))
                       for i in reqired_sg_to_del_array:
                           url = "http://%s/get_boxes?offset=0&limit=1000000&external_id=&mac_address=&service_group=0&only_overflowing=0&geo_id=%s" % (manager,str(i))
                           sg = urllib2.urlopen(url)
                           xml = sg.read()
                           sg_xml = libxml2.parseDoc(xml)
                           sg_list = sg_xml.xpathEval("//X/boxes/elem/box_data/external_id")                           
                           for url in sg_list:
                               sg_box = url.content
                               try:
                                   requests.delete('http://' + str(manager) + '/v2/homes/' + url.content)
                                   print "Delete Home ID - %s" % (str(url.content))
                                   counter_delete_home_id += 1
                                   if counter_delete_home_id >= num_of_delete:
                                       break
                               except:
                                   counter_delete_home_id += 1
                                   pass 
                                   
 
## if we delete using database:                          
    else:
        if remove_all_rsdvr == 'y':
            delete_home_id_by_proxy_db(manager, total_boxes_size ,0)
        else:
            delete_home_id_by_proxy_db(manager, num_of_delete, start_del_box_id)
                
if remove_channels == 'y' and not (is_proxy == 1 and is_rsdvr_rev3 ==2): 
    if (version_num[0] == 2) and (version_num[1] >= 6) and (version_num[3] >= 4) or (version_num[1] >= 7) or  (version_num[0] >= 3):        
        mgr_versions = 1
        if is_proxy == 0:
            url = "http://%s/multicast_channel/get_all?offset=0&limit=10000" % (manager)
            all_channels = urllib2.urlopen(url)
            xml = all_channels.read()
            channels_list = libxml2.parseDoc(xml)           
            delete_channels(manager, channels_list, "//X/value/channels/elem/name", num_of_delete_channels,mgr_versions)
        else: # this is proxy
            for i in range(len(managers)):
               url = "http://%s/multicast_channel/get_all?offset=0&limit=10000" % (managers[i])
               all_channels = urllib2.urlopen(url)
               xml = all_channels.read()
               channels_list = libxml2.parseDoc(xml)   
               delete_channels(managers[i], channels_list, "//X/value/channels/elem/name", num_of_delete_channels,mgr_versions) 
    else :        
        mgr_versions = 0
        if is_proxy == 0:
            url = "http://%s/multicast_channel/get_all?X=0" % (manager)
            all_channels = urllib2.urlopen(url)
            xml = all_channels.read()
            channels_list = libxml2.parseDoc(xml)           
            delete_channels(manager, channels_list, "//X/value/elem/name", num_of_delete_channels,mgr_versions)
        else: ##this is proxy
            for i in range(len(managers)):
                url = "http://%s/multicast_channel/get_all?X=0" % (manager[i])
                all_channels = urllib2.urlopen(url)
                xml = all_channels.read()
                channels_list = libxml2.parseDoc(xml) 
                delete_channels(managers[i], channels_list, "//X/value/elem/name", num_of_delete_channels,mgr_versions)
else:
    pass
   
        
    
if is_proxy == 0:
    print "\n\nFinished deleting :\n\t\t   RS-DVR boxes : %s\n\t\t   Channels : %s" %(counter_delete_home_id,counter_delete_channel )
else:
    print "\n\n\tProxy Env: \n\n\tFinished deleting :\n\n\t\t   RS-DVR boxes : %s\n\t\t   Channels(on all env') : %s" %(counter_delete_home_id,counter_delete_channel )
    if not (is_proxy == 1 or is_rsdvr_rev3 ==2):
        channels_list.freeDoc()
















