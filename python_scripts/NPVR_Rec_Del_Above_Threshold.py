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
import imp
import runpy
import subprocess
from tempfile import mkstemp
from shutil import move
from os import remove, close
import re
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////// this script creates NPVR V2 recordings (using the RSDVR_ingest.py script) - and delete recordings above "assets_to_leave" criteria///////////
#////////// set below - all ready assets from the script running time stamp and which exceeds the threshold of assets_to_leave - will be deleted/////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def replace(filename, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(filename)
    for line in old_file:
        #new_file.write(line.replace(pattern, subst))
        new_file.write(re.sub(pattern,subst,line))
    #close temp file
    new_file.close()
    close(fh)
    old_file.close()
    #Remove original file
    remove(filename)
    #Move new file
    move(abs_path, filename)



def main():
    manager_addr='10.10.61.22'
    manager_port='5929'
    db_addr = '10.10.61.21'
    db_machine_password = 'F@brix'
    time_to_run_in_sec = 60000
    assets_to_leave = 200
    total_num_of_ingests= 100000
    concurrent_ingests = 620 ## take into account the rolling buffer ingests
    start_time = 10
    end_time = 60
    is_rsdvr_rev3 = 3
## update the RSDVR_ingest ini file
    replace('RSDVR_ingest/conf/config.ini', "manager = .*", 'manager = %s:%s' % (str(manager_addr), str(manager_port)))
    replace('RSDVR_ingest/conf/config.ini', "total_ingests = .*", 'total_ingests = %s' % str(total_num_of_ingests))
    replace('RSDVR_ingest/conf/config.ini', "concurrent_ingests = .*", 'concurrent_ingests = %s' % str(concurrent_ingests))
    replace('RSDVR_ingest/conf/config.ini', "start_time = .*", 'start_time = %s' % str(start_time))
    replace('RSDVR_ingest/conf/config.ini', "end_time = .*", 'end_time = %s' % str(end_time))
    replace('RSDVR_ingest/conf/config.ini', "is_rsdvr_rev3 = .*", 'is_rsdvr_rev3 = %s' % str(is_rsdvr_rev3))
    
    
    #imp.load_source("RSDVR_ingest.py", "./RSDVR_ingest/src") 
    print "Starting to Schedule Recording"
    start_time=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    #os.chdir("./RSDVR_ingest/src")
    #subprocess.call("./RSDVR_ingest.py", shell=True)
#    subprocess.Popen(["pwd"])
#    os.chdir("./RSDVR_ingest/src/")
#    os.spawnl(os.P_NOWAIT, './RSDVR_ingest.py')
#    time.sleep(600000)
    proc = subprocess.Popen(["python RSDVR_ingest.py"], shell=True,cwd="./RSDVR_ingest/src")
    #stdout_value = proc.communicate()[0]
    #print '\tstdout:', repr(stdout_value)
    #os.chdir("../..")
    while time_to_run_in_sec > 0:
        print "time to run: " + str(time_to_run_in_sec)
        #time.sleep(1)
        time_to_run_in_sec -= 1
        x = '''expect -c "set timeout -1;
         spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select count\(*\) from asset where active=1 and ingesting=0 and data_type=2 and common_asset_id<>'' and update_time>'%s'\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
         match_max 100000;
         expect *password:*;
         send -- %s\\r;
         interact;" | grep -v "spawn\|password\|_abr" > count.tmp   '''  % (str(db_addr),str(start_time),str(db_machine_password))
        try:
            print x
            os.system(x)
        except:
             traceback.print_exc(file=sys.stdout)
        
        
        
        
        
        x = '''expect -c "set timeout -1;
         spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select external_id from asset where active=1 and ingesting=0 and data_type=2 and common_asset_id<>'' and update_time>'%s'\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
         match_max 100000;
         expect *password:*;
         send -- %s\\r;
         interact;" | grep -v "spawn\|password\|_abr" > assets.tmp   '''  % (str(db_addr),str(start_time),str(db_machine_password))
        try:
            print x
            os.system(x)
        except:
             traceback.print_exc(file=sys.stdout)
        file_count = open('count.tmp',"r")
        num_of_relevant_assets_in_db = file_count.readline()
        num_of_relevant_assets_in_db = str.strip(num_of_relevant_assets_in_db)
        #print num_of_relevant_assets_in_db
        num_of_asset_to_del= int(num_of_relevant_assets_in_db) - int(assets_to_leave)
        if num_of_asset_to_del <= 0:
            num_of_asset_to_del=0;
            continue
        else:
            pass 
        file_asset =  open('assets.tmp',"r")      
        lines = file_asset.readlines()
        for line in lines:
            if num_of_asset_to_del < 1:
                file_asset.close()
                file_count.close()
                break
            else:
                #if line.find('_abr') != -1:
                #    asset_id = str.strip(line[:line.rfind('_abr')])
                #else:
                    #url = "http://%s:%s/destroy_asset?asset_id=%s&type=0" % (str(manager_addr),str(manager_port),urllib.quote_plus(line))
                #    asset_id=line
                #print asset_id
                asset_id = line.strip()
                xml_msg = """<DeleteRecordings ShowingID="%s">
    <Homes>
<Home HomeID="%s" Type="0" />
   </Homes>
</DeleteRecordings>""" % (str(asset_id),"NPVR")
                headers = {'Content-Type' : 'text/x-xml2'}
                requests.post('http://' + str(manager_addr) + ":" + str(manager_port) + '/v2/recordings/delete/', data=xml_msg, headers=headers)                              
                num_of_asset_to_del -= 1
                #print num_of_asset_to_del
            
        



        

#    time.sleep(60)
    subprocess.call("for i in `ps -ef | grep RSDVR | grep -v grep |awk '{print $2}'` ; do echo \"avihu\" | sudo -S kill $i ; done", shell=True)
    x = '''expect -c "set timeout -1;
         spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select external_id from asset where active=1 and ingesting=0 and data_type=2 and common_asset_id<>'' and update_time>'%s'\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
         match_max 100000;
         expect *password:*;
         send -- %s\\r;
         interact;" | grep -v "spawn\|password\|_abr" > assets.tmp   '''  % (str(db_addr),str(start_time),str(db_machine_password))
    try:
        print x
        os.system(x)
    except:
        traceback.print_exc(file=sys.stdout)        
    file_asset =  open('assets.tmp',"r")      
    lines = file_asset.readlines()
    for line in lines:
        asset_id = line.strip()
        xml_msg = """<DeleteRecordings ShowingID="%s">
    <Homes>
<Home HomeID="%s" Type="0" />
   </Homes>
</DeleteRecordings>""" % (str(asset_id),"NPVR")
        headers = {'Content-Type' : 'text/x-xml2'}
        requests.post('http://' + str(manager_addr) + ":" + str(manager_port) + '/v2/recordings/delete/', data=xml_msg, headers=headers)                              
            
    file_asset.close()   
    os.system("find . -name 'assets.tmp'  | xargs rm" )
    os.system("find . -name 'count.tmp'  | xargs rm" )
    print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    
    
if __name__ == "__main__":
    main()
