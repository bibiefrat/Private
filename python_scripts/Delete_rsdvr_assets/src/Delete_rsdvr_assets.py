from configobj import ConfigObj
import libxml2
import logging
import os
import random
import signal
import string
import sys
import time
import urllib
import urllib2
import socket
import re
import requests
try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET

def send_url(url):
    """
    Send requests and handle exceptions
    """
    req = urllib2.Request(url)
    try:
        res = urllib2.urlopen(req).read()
    except urllib2.HTTPError, e:
        print 'Problem sending request:'
        print url
        print e
        sys.exit(1)
    except urllib2.URLError, e:
        print 'Problem sending request:'
        print url
        print e.reason
        sys.exit(1)
    return res
    
def checkByxPath(dom, xpath):   
                
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content

    return r

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


def del_from_home_v2(manager,initial_box_num,num_of_boxes,num_assets_to_delete,clean_home_ids,rsdvr_rev):
    global is_rsdvr_rev3,use_db,db_addr,db_machine_password,db_type,batch_size,batch_delete,delay_delete_batch
    
    if (is_rsdvr_rev3 == 4 or is_rsdvr_rev3 == 5):
        initial_box_num = "NPVR"
    
    if use_db != 1:
        for i in range(num_of_boxes):
            url = "http://%s/v2/subscribers/recordings/%s?State=6" % (manager,initial_box_num)
            try:
                all_rec_per_box = urllib2.urlopen(url)
                xml = all_rec_per_box.read()
                #print xml
                rec_id_list = libxml2.parseDoc(xml)
                print rec_id_list
                list = rec_id_list.xpathEval("//GetSubscriberRecordingsListReply/Recording")
                counter=1
                for node in list:
                    asset_id =  str(node.prop('ShowingID'))
                    try:
                        asset_state = str(node.xpathEval('./ABRDetails')[0].prop('State'))
                    except:
                        asset_state = str(node.xpathEval('./CBRDetails')[0].prop('State'))
                    if asset_state != '5':
                        if is_rsdvr_rev3 == 2:
                            xml_msg = """<DeleteRecordings ShowingID="%s">
                <Homes>
            <Home HomeID="%s" Type="0" />
               </Homes>
            </DeleteRecordings>""" % (str(asset_id),str(initial_box_num))
                            headers = {'Content-Type' : 'text/x-xml2'}
                        elif is_rsdvr_rev3 == 3 or is_rsdvr_rev3 == 5:
                            xml_msg = """<X>
        <size>2</size>
        <elem id="0">%s_abr$%s</elem>
        <elem id="1">%s_cbr$%s</elem>
    </X>""" % (str(asset_id),str(initial_box_num),str(asset_id),str(initial_box_num))
                            headers = {'Content-Type' : 'text/xml'}
                        if batch_delete == 'y' and counter == batch_size:
                            time.sleep(delay_delete_batch)
                            print counter
                            counter = 0
                        else:
                            pass
                        counter +=1
                        if is_rsdvr_rev3 == 2:                       
                            r = requests.post('http://' + str(manager) + '/v2/recordings/delete/', data=xml_msg, headers=headers)
                        elif is_rsdvr_rev3 == 3 or is_rsdvr_rev3 == 5:
                            r = requests.post('http://' + str(manager) + '/destroy_multiple_asset', data=xml_msg, headers=headers)
                        print "delete %s box %s" % (str(asset_id),str(initial_box_num))
                        print "reply %s" % (str(r))
            except:
                pass
            if (is_rsdvr_rev3 == 4 or is_rsdvr_rev3 == 5):
                break
            else:
                initial_box_num += 1
    elif  use_db == 1:
        os.system("find . -name 'rsdvr_asset.list'  | xargs rm" )
        if not (is_rsdvr_rev3 == 4 or is_rsdvr_rev3 == 5):
            max_box_id=initial_box_num+num_of_boxes
            if db_type == 'solid':
                x = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select A.external_id from asset A join rsdvr_box B on A.box_id=B.id where A.data_type in (1,3)  and B.external_id<>'NPVR' and (cast(B.external_id as integer)) >= %s and (cast(B.external_id as integer)) < %s and A.active='1'\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | grep -v "spawn\|password"  > rsdvr_asset.list  '''  % (str(db_addr),str(initial_box_num),str(max_box_id),str(db_machine_password))   
                try:
                    print x
                    os.system(x)
                except:
                     traceback.print_exc(file=sys.stdout)
            elif db_type == 'postgres':
                x = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"for i in $\(seq 1 1\); do \(PGPASSWORD=fabrix psql -t -U fabrix -d manager -h %s -p 9999 -c  \\\\\\"select A.external_id from asset A join rsdvr_box B on A.box_id=B.id where A.data_type in (1,3)  and B.external_id<>'NPVR' and (cast(B.external_id as integer)) >= %s and (cast(B.external_id as integer)) < %s and A.active='1'\\\\\\" ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | grep -v "spawn\|password"  > rsdvr_asset.list  '''  % (str(db_addr),str(db_addr),str(initial_box_num),str(max_box_id),str(db_machine_password))   
                try:
                    print x
                    os.system(x)
                except:
                     traceback.print_exc(file=sys.stdout)
        else: ## NPVR recording
            if db_type == 'solid':
                x = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select external_id from asset where asset.data_type=2 and ext_related_asset_id is null and ext_relation_type=0 and active=1\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | grep -v "spawn\|password" | grep "_abr\|_cbr\|REASSET_" > rsdvr_asset.list  '''  % (str(db_addr),str(db_machine_password))   
                try:
                    print x
                    os.system(x)
                except:
                     traceback.print_exc(file=sys.stdout)
            elif db_type == 'postgres':
                x = '''expect -c "set timeout -1;
                 spawn ssh %s -l root \\"for i in $\(seq 1 1\); do \(PGPASSWORD=fabrix psql -t -U fabrix -d manager -h %s -p 9999 -c  \\\\\\"select external_id from asset where asset.data_type=2 and ext_related_asset_id is null and ext_relation_type=0 and active=1\\\\\\" ;sleep 1 \); done; exit;\\";
                 match_max 100000;
                 expect *password:*;
                 send -- %s\\r;
                 interact;" | grep -v "spawn\|password" | grep "_abr\|_cbr\|REASSET_" > rsdvr_asset.list  '''  % (str(db_addr),str(db_addr),str(db_machine_password))   
                try:
                    print x
                    os.system(x)
                except:
                     traceback.print_exc(file=sys.stdout)            
            
            
            
        lines = open('rsdvr_asset.list', "r").readlines()
        counter = 1
        for line in lines:
            if line.find('_cbr') != -1 or line.find('_abr') != -1 or line.find('REASSET_') != -1:
                if line.find('_cbr') != -1:
                    asset_id = str.strip(line[:line.rfind('_cbr')])
                if line.find('_abr') != -1:
                    asset_id = str.strip(line[:line.rfind('_abr')])
                if line.find('REASSET_') != -1:
                    asset_id = str(line).strip()
            else:                    
                asset_id = str.strip(line[line.find('_') + 1:line.rfind('$')])
            if line.find(' ') != 0:
                home_id =  str.strip(line[line.find('$') + 1:line.find(' ')])
            elif line.find('\r\n') != 0:
                home_id =  str.strip(line[line.find('$') + 1:line.find('\r\n')])
            if is_rsdvr_rev3 == 2:    
                xml_msg = """<DeleteRecordings ShowingID="%s" Type="1">
                <Homes>
            <Home HomeID="%s" Type="0" />
               </Homes>
            </DeleteRecordings>""" % (str(asset_id),str(home_id))
                headers = {'Content-Type' : 'text/x-xml2'}
 
            if is_rsdvr_rev3 == 4:    
                xml_msg = """<DeleteRecordings ShowingID="%s" Type="1">
                <Homes>
            <Home HomeID="%s" Type="0" />
               </Homes>
            </DeleteRecordings>""" % (str(asset_id),str("NPVR"))
                headers = {'Content-Type' : 'text/x-xml2'}               
                
                
            elif is_rsdvr_rev3 == 3 or is_rsdvr_rev3 == 5:
                xml_msg = """<X>
        <size>2</size>
        <elem id="0">%s_abr$%s</elem>
        <elem id="1">%s_cbr$%s</elem>
    </X>""" % (str(asset_id),str(initial_box_num),str(asset_id),str(initial_box_num))
                headers = {'Content-Type' : 'text/xml'}
                
            if batch_delete == 'y' and counter == batch_size:
                time.sleep(delay_delete_batch)
                print counter
                counter = 0
            else:
                pass
            counter +=1
            if is_rsdvr_rev3 == 2 or is_rsdvr_rev3 == 4:
                reply = requests.post('http://' + str(manager) + '/v2/recordings/delete/', data=xml_msg, headers=headers)
                print "reply: " + str(reply.text)
            elif is_rsdvr_rev3 == 3 or is_rsdvr_rev3 == 5:
                requests.post('http://' + str(manager) + '/destroy_multiple_asset', data=xml_msg, headers=headers)
            print "delete %s box %s" % (str(asset_id),str(home_id))            
        os.system("find . -name 'rsdvr_asset.list'  | xargs rm" )
                 
#            print home_id
#            print asset_id
        
def del_from_home(manager,initial_box_num,num_of_boxes,num_assets_to_delete,clean_home_ids,rsdvr_rev):
    global is_rsdvr_rev3   
    if write_asset_file == "y" :
        asset_file = open("asset.list","a")
    if use_db == 1:
        os.system("find . -name 'rsdvr_asset.list'  | xargs rm" )
        max_box_id=initial_box_num+num_of_boxes
        if db_type == 'solid':
            x = '''expect -c "set timeout -1;
             spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -x onlyresults -e \\\\\\"select A.external_id from asset A join rsdvr_box B on A.box_id=B.id where A.data_type in (1,3)  and B.external_id<>'NPVR' and (cast(B.external_id as integer)) >= %s and (cast(B.external_id as integer)) < %s and A.active='1'\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
             match_max 100000;
             expect *password:*;
             send -- %s\\r;
             interact;" | grep -v "spawn\|password"  > rsdvr_asset.list  '''  % (str(db_addr),str(initial_box_num),str(max_box_id),str(db_machine_password))   
            try:
                print x
                os.system(x)
            except:
                 traceback.print_exc(file=sys.stdout)    
        if db_type == 'postgres':            
            x = '''expect -c "set timeout -1;
             spawn ssh %s -l root \\"for i in $\(seq 1 1\); do \(PGPASSWORD=fabrix psql -t -U fabrix -d manager -h %s -p 9999 -c  \\\\\\"select A.external_id from asset A join rsdvr_box B on A.box_id=B.id where A.data_type in (1,3)  and B.external_id<>'NPVR' and (cast(B.external_id as integer)) >= %s and (cast(B.external_id as integer)) < %s and A.active='1'\\\\\\"  ;sleep 1 \); done; exit;\\";
             match_max 100000;
             expect *password:*;
             send -- %s\\r;
             interact;" | grep -v "spawn\|password"  > rsdvr_asset.list  '''  % (str(db_addr),str(db_addr),str(initial_box_num),str(max_box_id),str(db_machine_password))   
            try:
                print x
                os.system(x)
            except:
                 traceback.print_exc(file=sys.stdout)    
    
    
    
    for i in range(num_of_boxes):
        url = "http://%s/%s?type=GetHomeProfileDetails&HomeID=%s" % (manager,rsdvr_rev,initial_box_num)
        #print "Box num: " + str(initial_box_num)
        try:
            all_rec_per_box = urllib2.urlopen(url)
            xml = all_rec_per_box.read()
            rec_id_list = libxml2.parseDoc(xml)
            if is_rsdvr_rev3 == 0:
                list = rec_id_list.xpathEval("//HomeProfileDetails/AssetList/AssetInfo")
            elif is_rsdvr_rev3 == 1:
                records_str = send_url("http://%s/%s?type=GetHomeProfileDetails&HomeID=%s" % (str(manager),str(rsdvr_rev),str(initial_box_num)))
                records_xml = ET.fromstring(records_str)
                #recording = records_xml.find("RecordingList")
                list = records_xml.findall(".//{http://iplatform.cablevision.com/namespaces/dvrplus/scheduler}Recording")
               #for e in list:
                #    print e.get("AssetID")
                #list = rec_id_list.getRootElement().get_children().get_next().get_children()        
            counter_asset = 1
            msg = ""
            POSTmsg = ""
            asset_count = 0
            if clean_home_ids == 'n':            
                for node in list:
                    if is_rsdvr_rev3 == 0:
                        asset_id = str.strip(  str(node)[ str(node).find("AssetID", 0) + 9: str(node).find("ReasonCode", 0) -2]    )
                    elif is_rsdvr_rev3 == 1:
                        asset_id = node.get("AssetID")
                        
                    #print("%s") % str(asset_id)                
                    if (counter_asset <= num_assets_to_delete) or  (num_assets_to_delete == 0):                    
                        asset_id = urllib.quote_plus(asset_id)                        
                        url = "http://%s/get_asset_properties?external_id=2_%s$%s&internal_id=0" % (manager,asset_id,initial_box_num)
                        #print url
                        all_asset_info = urllib2.urlopen(url)
                        xml = all_asset_info.read()           
                        all_asset_list = libxml2.parseDoc(xml)
                        
                        real_asset_state = int(get_info_asset(manager, all_asset_list, "/X/state"))
                        asset_duration = int(get_info_asset(manager, all_asset_list, "/X/act_duration"))
                        asset_request_time = float(get_info_asset(manager, all_asset_list, "/X/request_time"))
                        asset_request_time_int = int(round(asset_request_time))
                        #print asset_request_time_int
                        #print "asset = 2_%s$%s , state = %s" % (asset_id,initial_box_num ,real_asset_state)
                        
                        if ((delete_asset_state.has_key(real_asset_state)) and (duration_asset_2_del <= asset_duration)) :
                            url = "http://%s/destroy_asset?asset_id=2_%s$%s&type=%s" % (manager, asset_id,initial_box_num,str(soft_delete))
                            POSTmsg = '<?xml version="1.0" encoding="utf-8"?><DeleteRecordingsByHome HomeID = "%s"> <RecordingList>' % str(initial_box_num)
                            POSTmsg += '<Recording  AssetID="%s" />' % (str(asset_id))
                            POSTmsg += '</RecordingList></DeleteRecordingsByHome>'
                            if write_asset_file == 'y' : 
                                print "Adding asset 2_%s$%s to asset.list file" % (asset_id,initial_box_num)
                                asset_file.write("2_%s$%s\n" % (asset_id,initial_box_num))
                                #count_lines = len(asset_file.readlines())
                                #print "# of lines in file --> %s" %(count_lines)
                            
                            else :
                                if batch_delete == 'n' :
                                    try:
                                        if delete_by_http == 1:
                                            print "Delete asset url --> %s\n" %(url)
                                            delete_asset = urllib2.urlopen(url)
                                            xml_delete = delete_asset.read()
                                            delete_xml_doc = libxml2.parseDoc(xml_delete)
                                            error_desc = delete_error_parse(manager, delete_xml_doc, "//code")
                                            if "Asset deleted successfully" in error_desc:
                                                print error_desc + "\n"
                                            else :
                                                print "The asset %s couldn't be deleted because : 2_%s$%s" % (asset_id,initial_box_num, error_desc)
                                            ##
                                        elif delete_by_http == 0:                    
                                            print "send xml:\n" + str(POSTmsg)                                            
                                            
                                            manager_ip = manager[:string.find(manager,":")]
                                            manager_port = int(manager[string.find(manager,":") + 1:])
                                            length=len(POSTmsg)  
                                            #print "length --> ", length
                                            
                                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                            
                                            s.connect((manager_ip,manager_port ))
                                            s.send("POST /%s HTTP/1.0\r\n" % (rsdvr_rev))
                                            s.send("Content-Type: text/xml\r\n")
                                            s.send("Content-Length: "+str(length)+"\r\n\r\n")
                                        
                                            try : 
                                                s.sendall(POSTmsg)
                                                datarecv=s.recv(1024)
                                                print "Reply Received: "+ str(datarecv)
                                            except socket.error,message :
                                                print "!!!!! Message was not sent due to the following socket error : %s !!!!!!\n " % (str(message))
                                                pass                                            
                                            s.close()
                                            POSTmsg = ""
                                    except :
                                        print "Couldn't delete asset 2_%s$%s" % (asset_id,initial_box_num)
                                
                                else :   
                                    # preparing the array for later delete
                                    print "Adding asset 2_%s$%s to array" % (asset_id,initial_box_num)
                                    array_delete.append("2_" + asset_id + "$" + str(initial_box_num))
                        all_asset_list.freeDoc()
                    if num_assets_to_delete != 0 :
                            counter_asset += 1
                            
            elif clean_home_ids == 'y':
                if use_db == 0:
                    for node in list:
                        asset_id = str.strip(  str(node)[ str(node).find("AssetID", 0) + 9: str(node).find("ReasonCode", 0) -2]    )
                        #print("%s") % str(asset_id)
                        asset_count += 1                  
                        msg +=  "&AssetID=%s" % (str(asset_id))
                        if is_rsdvr_rev3 == 0:
                            POSTmsg += '<AssetListItem  AssetID="%s" />' % (str(asset_id))
                        elif is_rsdvr_rev3 == 1:
                            POSTmsg += '<Recording  AssetID="%s" />' % (str(asset_id))
                        if write_asset_file == 'y':
                            asset_file.write("2_%s$%s\n" % (asset_id,initial_box_num))
                    if is_rsdvr_rev3 == 0:                            
                        url = "http://%s/RSDVR?type=DeleteRecordingsByHome&HomeID=%s&size=%s%s" % (str(manager),str(initial_box_num),str(asset_count),str(msg))
                        POSTmsg = '<?xml version="1.0" encoding="utf-8"?><DeleteRecordingsByHome HomeID = "%s"> <AssetList>%s</AssetList></DeleteRecordingsByHome>' % (str(initial_box_num) ,str(POSTmsg))
                    else:
                        url = "http://%s/Rev3_RSDVR?type=DeleteRecordingsByHome&HomeID=%s&size=0&size=%s%s" % (str(manager),str(initial_box_num),str(asset_count),str(msg)) 
                        POSTmsg = '<?xml version="1.0" encoding="utf-8"?><DeleteRecordingsByHome HomeID = "%s"> <RecordingList>%s</RecordingList></DeleteRecordingsByHome>' % (str(initial_box_num) ,str(POSTmsg))
                    if delete_by_http == 1: 
                        print url
                    else:
                        #print ("POST /%s HTTP/1.0\r\n" % str(rsdvr_rev))
                        #print("Content-Type: text/xml\r\n")
                        #print("Content-Length: "+str(len(POSTmsg))+"\r\n\r\n")
                        print str(POSTmsg)
                else: # use DB == 1
                    
                    os.system("cat rsdvr_asset.list | grep -i \"\\$%s \" > temp_recording.list" % str(initial_box_num))
                    lines = open('temp_recording.list',"r").readlines()
                    count = 0
                    for line in lines:
                        if line.find('_cbr') != -1:
                            asset_id = str.strip(line[:line.rfind('_cbr')])
                        if line.find('_abr') != -1:
                            asset_id = str.strip(line[:line.rfind('_abr')])
                        else:                    
                            asset_id = str.strip(line[line.find('_') + 1:line.rfind('$')])
                        home_id =  str.strip(line[line.find('$') + 1:line.find(' ')])
                        asset_count += 1                  
                        msg +=  "&AssetID=%s" % (str(asset_id))
                        if is_rsdvr_rev3 == 0:
                            POSTmsg += '<AssetListItem  AssetID="%s" />' % (str(asset_id))
                        elif is_rsdvr_rev3 == 1:
                            POSTmsg += '<Recording  AssetID="%s" />' % (str(asset_id))
                        if write_asset_file == 'y':
                            asset_file.write("2_%s$%s\n" % (asset_id,initial_box_num))
                    if is_rsdvr_rev3 == 0:                            
                        url = "http://%s/RSDVR?type=DeleteRecordingsByHome&HomeID=%s&size=%s%s" % (str(manager),str(initial_box_num),str(asset_count),str(msg))
                        POSTmsg = '<?xml version="1.0" encoding="utf-8"?><DeleteRecordingsByHome HomeID = "%s"> <AssetList>%s</AssetList></DeleteRecordingsByHome>' % (str(initial_box_num) ,str(POSTmsg))
                    else:
                        url = "http://%s/Rev3_RSDVR?type=DeleteRecordingsByHome&HomeID=%s&size=0&size=%s%s" % (str(manager),str(initial_box_num),str(asset_count),str(msg)) 
                        POSTmsg = '<?xml version="1.0" encoding="utf-8"?><DeleteRecordingsByHome HomeID = "%s"> <RecordingList>%s</RecordingList></DeleteRecordingsByHome>' % (str(initial_box_num) ,str(POSTmsg))
                    if delete_by_http == 1: 
                        print url
                    else:
                        #print ("POST /%s HTTP/1.0\r\n" % str(rsdvr_rev))
                        #print("Content-Type: text/xml\r\n")
                        #print("Content-Length: "+str(len(POSTmsg))+"\r\n\r\n")
                        print str(POSTmsg)
                        
                        
                        
                    os.system("find . -name 'temp_recording.list'  | xargs rm" )                    
                    
                    
                    
                    
                
                if write_asset_file == 'n':
                    if delete_by_http == 1:
                        delete_asset = urllib2.urlopen(url)
                        xml_delete = delete_asset.read()
                        delete_xml_doc = libxml2.parseDoc(xml_delete)
                    elif  delete_by_http == 0:
                         #print "send xml:\n" + str(POSTmsg)
                         manager_ip = manager[:string.find(manager,":")]
                         manager_port = int(manager[string.find(manager,":") + 1:])
                         length=len(POSTmsg)  
                       #print "length --> ", length
                       
                         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                            
                         s.connect((manager_ip,manager_port ))
                         s.send("POST /%s HTTP/1.0\r\n" % str(rsdvr_rev))
                         s.send("Content-Type: text/xml\r\n")
                         s.send("Content-Length: "+str(length)+"\r\n\r\n")
                         try : 
                             s.sendall(POSTmsg)
                             datarecv=s.recv(1024)
                             print "Reply Received: "+ str(datarecv)
                         except socket.error,message :
                             print "!!!!! Message was not sent due to the following socket error : %s !!!!!!\n " % (str(message))
                             pass                                            
                         s.close()
                         POSTmsg = ""
            asset_count = 0
            initial_box_num += 1    
        except:
            initial_box_num += 1
            pass   
    if write_asset_file == "y" :                
        asset_file.close()     
    os.system("find . -name 'rsdvr_asset.list'  | xargs rm" )       
            



def get_boxes_list(manager,dom, xpath, all_list_asset, asset_state, num_of_boxes, num_assets_to_delete): 
    

    #print manager, dom, xpath, all_list_asset, asset_state, initial_box_num, num_of_boxes , num_assets_to_delete  
    list = dom.xpathEval(xpath)    
    if all_list_asset == 'y' :
        for node in list:
           if node.content != '0' :     
               recordings_list(manager, node.content,node.next.next.next.next.next.next.next.next.content, num_assets_to_delete)
        
#    else :
#        index=1
#        for node in list:
#            if index <= num_of_boxes:
#                #print "node = %s, index = %s" % (node.content,index)
#                if (node.content != '0') and (int(node.content) >= int(initial_box_num)) : 
#                    #print "****\nnode = " + str(node)       
#                    recordings_list(manager, node.content,node.next.next.next.next.next.next.content, num_assets_to_delete)
#                    index += 1            
#                

def recordings_list(manager, node_content, home_id, num_assets_to_delete):
    rec_id_list = None
    try:
        try :
            # Opening the XML of the recordings per box
            url = "http://%s/box_asset_list?id=%s&stb_addr=0" % (manager,urllib.quote_plus (node_content))
            #print "url = " + url
            all_rec_per_box = urllib2.urlopen(url)
            xml = all_rec_per_box.read()
            rec_id_list = libxml2.parseDoc(xml)
            # delete using the FX help
            if delete_by_http == 1 :
                get_recordings_per_boxes(manager,rec_id_list, "//X/elem/external_id", num_assets_to_delete)
            elif delete_by_http == 0 :
                # Delete via post
                delete_recording_per_boxes_POST(manager,rec_id_list, "//X/elem/external_id", home_id)
            else :
                log.info("Wrong parameter : http / post delete (delete_by_http = 1/0 ")
            
        except urllib2.URLError, err:
            print "Couldn't open URL for delete .\n url : %s . \n Manager Error : %s ." % (url, err.reason)
    finally:
        if rec_id_list:
            rec_id_list.freeDoc()
    
    return ()
           
    
    
def get_recordings_per_boxes(manager,dom, xpath, num_assets_to_delete):
    
    global array_delete
    global delete_asset_state
    global duration_asset_2_del
    
    
    if write_asset_file == "y" :
        asset_file = open("asset.list","a")
    #print manager, xpath,num_home_id     
    list = dom.xpathEval(xpath)
    
    counter_asset = 1    
    for node in list:
        if (counter_asset <= num_assets_to_delete) or  (num_assets_to_delete == 0):
            #print node.content
            node.content = urllib.quote_plus(node.content)
            #print node.content
            url = "http://%s/get_asset_properties?external_id=%s&internal_id=0" % (manager, node.content)
            #print url
            all_asset_info = urllib2.urlopen(url)
            xml = all_asset_info.read()           
            all_asset_list = libxml2.parseDoc(xml)
            
            real_asset_state = int(get_info_asset(manager, all_asset_list, "/X/state"))
            asset_duration = int(get_info_asset(manager, all_asset_list, "/X/act_duration"))
            asset_request_time = float(get_info_asset(manager, all_asset_list, "/X/request_time"))
            asset_request_time_int = int(round(asset_request_time))
            #print asset_request_time_int
            print "asset = %s , state = %s" % (node.content, real_asset_state)
            
            if ((delete_asset_state.has_key(real_asset_state)) and (duration_asset_2_del <= asset_duration)) :
                url = "http://%s/destroy_asset?asset_id=%s&type=$s" % (manager, node.content,str(soft_delete))
                if write_asset_file == 'y' : 
                    print "Adding asset %s to asset.list file" % (node.content)
                    asset_file.write("%s\n" % (node.content))
                    #count_lines = len(asset_file.readlines())
                    #print "# of lines in file --> %s" %(count_lines)
                
                else :
                    if batch_delete == 'n' :
                        try:
                            print "Delete asset url --> %s\n" %(url)
                            delete_asset = urllib2.urlopen(url)
                            xml_delete = delete_asset.read()
                            delete_xml_doc = libxml2.parseDoc(xml_delete)
                            error_desc = delete_error_parse(manager, delete_xml_doc, "//code")
                            if "Asset deleted successfully" in error_desc:
                                print error_desc + "\n"
                            else :
                                print "The asset %s couldn't be deleted because : %s" % (node.content, error_desc)
                            
                        except :
                            print "Couldn't delete asset %s" % (node.content)
                    
                    else :   
                        # preparing the array for later delete
                        print "Adding asset %s to array" % (node.content)
                        array_delete.append(node.content)
            all_asset_list.freeDoc()
        if num_assets_to_delete != 0 :
            counter_asset += 1        
    if write_asset_file == "y" :                
        asset_file.close()

def CreateUrl_delete (params, length):
    url = "http://%s/destroy_multiple_asset" % ( manager)
    url += "?size=%s%s" %((str(length)),params)
    delete_xml_doc = None
    try: 
        try:
            print "Sending multiple HTTP deletes : \nurl --> %s" % (url)
            delete_asset = urllib2.urlopen(url)
            xml_delete = delete_asset.read()
            delete_xml_doc = libxml2.parseDoc(xml_delete)
            error_desc = delete_error_parse(manager, delete_xml_doc, "//code")
            #if "Asset deleted successfully" in error_desc:
            #    print error_desc + "\n"
            #else :
            #    print "Delete failed because : \n\t%s\n" % (i, error_desc)
        except :
            if del_assets_from_file == 'y' :
                print "Couldn't delete from file assets :\n %s\n" % (params)
            else :
                print "Couldn't delete assets :\n %s\n" % (params)
    finally:
        if delete_xml_doc:
            delete_xml_doc.freeDoc()
 

def get_info_asset (manager, dom, xpath):
    
    list = dom.xpathEval(xpath)
    for node in list:
        r = node.content
    delete_recording_per_boxes_POST
    return r

def delete_error_parse (manager, dom, xpath):

    list = dom.xpathEval(xpath)
    for node in list:
        if int(node.content) != 0 :
            error = node.next.next.content
        else :
            error = "Asset deleted successfully"

    return error

def get_internal_box_id(manager, dom, xpath, initial_box_num):  

    list = dom.xpathEval(xpath)
    for node in list:
        if (node.content != 'NPVR') and (node.content != 'Pause') and (int(node.content) == initial_box_num) :
            #print "*******\ninternal ID --> %s\n********" % (node.prev.prev.prev.prev.prev.prev.content)
            return node.prev.prev.prev.prev.prev.prev.prev.prev.content
    return -1;

def asset_list_creation_time(manager, dom, xpath):
    global batch_delete
    global array_delete,is_rsdvr_rev3
    
    list = dom.xpathEval(xpath)
    for node in list:
        if batch_delete == "n" or is_rsdvr_rev3 == 2:
            r = re.compile('.*\$.+\$.*')
            if r.match(node.content) != None:
                home_id=node.content [node.content.find("$") + 1:node.content.rfind("$")]
                continue
            else:
                asset_id=node.content
                home_id = node.content [node.content.find("$") + 1:]
            url = "http://%s/destroy_asset?asset_id=%s&type=%s" % (manager,urllib.quote_plus ( asset_id),str(soft_delete))
            try:
                if is_rsdvr_rev3 != 2:
                    print "Delete asset url --> %s\n" %(url)
                    delete_asset = urllib2.urlopen(url)
                else:                   
                    if asset_id.find('_cbr') != -1:
                        asset_id = str.strip(asset_id[:asset_id.rfind('_cbr')])
                    elif asset_id.find('_abr') != -1:
                        asset_id = str.strip(asset_id[:asset_id.rfind('_abr')])
                    xml_msg = """<DeleteRecordings ShowingID="%s">
    <Homes>
<Home HomeID="%s" Type="0" />
   </Homes>
</DeleteRecordings>""" % (str(asset_id),str(home_id))
                    headers = {'Content-Type' : 'text/x-xml2'}
                    requests.post('http://' + str(manager) + '/v2/recordings/delete/', data=xml_msg, headers=headers)
                    
            except :
                print "couldn't delete %s" % (asset_id)
        
        else : # prepare array_delete
            print "Adding asset %s to array" % urllib.quote_plus ((node.content))
            array_delete.append(asset_id)

def create_random_array():
    global array_delete
    rand_array = []
    array_size = len(array_delete)
    current_array_length = array_size
    index = 0
    for i in range (array_size):
        index = random.randint(0,current_array_length - 1)
        #print current_array_length
        #print array_delete[index]
        rand_array.append(array_delete[index]) 
        array_delete[index] = array_delete[current_array_length - 1]
        current_array_length = current_array_length - 1
    array_delete = rand_array      
    return  array_delete

def delete_recording_per_boxes_POST (manager,dom, xpath,home_id):
    global array_delete
    global delete_asset_state
    global duration_asset_2_del
    global success_ingests
    global failed_ingests 
    global rsdvr_rev
    global is_rsdvr_rev3
    
    counter = 0
    if write_asset_file == "y" :
        asset_file = open("asset.list","a")
    #print manager, xpath,num_home_id
    if is_rsdvr_rev3==0:
        msg = '<?xml version="1.0" encoding="utf-8"?><DeleteRecordingsByHome HomeID = "%s"> <AssetList>' % str(home_id)
    elif is_rsdvr_rev3==1:
        msg = '<?xml version="1.0" encoding="utf-8"?><DeleteRecordingsByHome HomeID = "%s"> <RecordingList>' % str(home_id)
      
    list = dom.xpathEval(xpath)
    for node in list:
        #print node.content
        url = "http://%s/get_asset_properties?external_id=%s&internal_id=0" % (manager, node.content)
        #print url
        all_asset_info = urllib2.urlopen(url)
        xml = all_asset_info.read()        
        all_asset_list = libxml2.parseDoc(xml)
        
        real_asset_state = int(get_info_asset(manager, all_asset_list, "/X/state"))
        asset_duration = int(get_info_asset(manager, all_asset_list, "/X/act_duration"))
        asset_request_time = float(get_info_asset(manager, all_asset_list, "/X/request_time"))
        asset_request_time_int = int(round(asset_request_time))
        #print asset_request_time_int
        print "asset = %s , state = %s" % (node.content, real_asset_state)
        
        
        asset_id = node.content[2:string.find(node.content, "$")]
        if ((delete_asset_state.has_key(real_asset_state)) and (duration_asset_2_del <= asset_duration)) :
            if is_rsdvr_rev3==0:
                msg += '<AssetListItem  AssetID="%s" />' % (str(asset_id))
            elif is_rsdvr_rev3==1:
                msg += '<Recording  AssetID="%s" />' % (str(asset_id))
            counter += 1
            if write_asset_file == 'y' : 
                print "Adding asset 2_%s$%s to asset.list file" % (str(asset_id),str(home_id))
                asset_file.write("2_%s$%s\n" % (str(asset_id),str(home_id)))
             
        all_asset_list.freeDoc()
    if is_rsdvr_rev3==0:
        msg += '</AssetList></DeleteRecordingsByHome>'
    elif is_rsdvr_rev3==1:
        msg += '</RecordingList></DeleteRecordingsByHome>'
    
    print "send xml:\n" + msg
    print_errors=int(1)
    
    
    if write_asset_file == 'n' :
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
            print "!!!!! Message was not sent due to the following socket error : %s !!!!!!\n " % (str(message))
            pass
        s.close()
        time_after_closing_socket = time.time()
        close_socket_time = time_after_closing_socket - initial_time
        print "Closing socket time : %s\n" % (close_socket_time)
    if write_asset_file == "y" :                
        asset_file.close()
    return 
     
# ------------------------------------------------------
# Main

# Getting current folder location
#path = os.getcwd()
path = "../"
success_ingests = 0
failed_ingests = 0 


# Reading configuration file
config = ConfigObj(path+'/conf/config.ini')

log_file = str(config['Configuration']['log_file']).strip()
log_level = str(string.upper(config['Configuration']['desired_log_level']).strip())
manager = str(config['Configuration']['manager']).strip()
all_list_asset = str(config['Configuration']['all_list_asset'])
initial_box_num = int(str(config['Configuration']['initial_box_num']).rstrip())
num_of_boxes = int(str(config['Configuration']['num_of_boxes']).rstrip())
asset_state = config['Configuration']['asset_state']
duration_asset_2_del = int(str(config['Configuration']['duration_asset_2_del']).rstrip())
del_from_time = int(str(config['Configuration']['del_from_time']).rstrip())
reference_apoc_point = str(config['Configuration']['reference_apoc_point']).strip()
batch_delete = str(config['Configuration']['batch_delete']).strip()
batch_size = int(str(config['Configuration']['num_batch_to_delete']).strip())
num_assets_to_delete = int(str(config['Configuration']['num_assets_to_delete']).strip())
delay_delete_batch = int(str(config['Configuration']['delay_delete_batch']).strip())
write_asset_file = str(config['Configuration']['write_asset_file']).strip()
del_assets_from_file = str(config['Configuration']['del_assets_from_file']).strip()
rand = int(str(config['Configuration']['rand']).strip())
delete_by_http = int(str(config['Configuration']['delete_by_http']).strip())
total_num_of_asset_to_delete = int(str(config['Configuration']['total_num_of_asset_to_delete']).strip())
clean_home_ids = str(config['Configuration']['clean_home_ids']).strip()
is_rsdvr_rev3 = int(str(config['Configuration']['is_rsdvr_rev3']).strip())
use_db = int(str(config['Configuration']['use_db']).strip())
db_addr = str(str(config['Configuration']['db_addr']).strip())
db_machine_password = str(str(config['Configuration']['db_machine_password']).strip())
soft_delete = int(str(config['Configuration']['soft_delete']).strip())
db_type = str(str(config['Configuration']['db_type']).strip())
#----------------------------------------------------------------

if is_rsdvr_rev3==0:
    rsdvr_rev='RSDVR'
elif is_rsdvr_rev3==1:
    rsdvr_rev='Rev3_RSDVR'
elif is_rsdvr_rev3==2 or is_rsdvr_rev3==3 or is_rsdvr_rev3==4 or is_rsdvr_rev3==5:
    rsdvr_rev='v2'
else:
    print ' ---------------------------------- invalid RSDVR revision -----------------------------------'
                    

# Switching the asset state to integer numbers
if len(asset_state) > 1 :
    for i in range(len(asset_state)):
        asset_state[i] = int(asset_state[i])
else :
    asset_state[0] = int(asset_state[0])
    
array_delete = []

#prepare dictionary for requested asset state to delete
delete_asset_state = {}
for i in range(len(asset_state)) :
    delete_asset_state[asset_state[i]] = int(asset_state[i])


defineLogger()
log = logging.getLogger('Main')


#if del_from_time == 0 and is_rsdvr_rev3 !=2:
if del_from_time == 0:
    log.info("Starting to Delete RS-DVR assets using http (fxhelp) method ...\n\n\n")
           
    if del_assets_from_file == 'n' :
        # Deleting current asset.list file
        try:
            x = os.path.exists("asset.list")
            if x == True :
                print "Removing old asset.list file...\n"
                z = os.remove("asset.list")
            else:
                print "File asset.list does not exist. Will create a new file"
    
        except:
            pass
        
        # Opening the XML of the home_id's list
        url = "http://%s/get_boxes?offset=0&limit=100" % (manager)
        #print "url = " + url
        all_home_id = urllib2.urlopen(url)
        xml = all_home_id.read()
        #home_id_list.freeDoc()
        home_id_list = libxml2.parseDoc(xml)
        #print "boxes-list -->" + str(home_id_list)
        total_boxes_size = int(checkByxPath(home_id_list, "/X/total_count"))
        print "Total_number of boxes in the system : %s \n" % (total_boxes_size)
        #finding internal ID of initial_box_number
#            box_fetch = 100 
#            for i in range (1 ,(total_boxes_size / 100) + 2) :
#                if i == 1 :
#                    current_range = 0
#            
#                #finding internal ID of initial_box_number
#                temp_internal_initial_box_num = get_internal_box_id(manager, home_id_list, "//X/boxes/elem/external_id", initial_box_num)
#                
#                #if batch_delete == 'n' :
#                if temp_internal_initial_box_num != -1 :
#                    internal_initial_box_num = temp_internal_initial_box_num            
#                else:
#                    pass
#        
#                url = "http://%s/get_boxes?offset=%s&limit=100" % (manager, box_fetch)
#                #print "url = " + url
#                all_home_id = urllib2.urlopen(url)
#                xml = all_home_id.read()
#                home_id_list.freeDoc()
#                home_id_list = libxml2.parseDoc(xml)
#                current_range += 100
#                box_fetch += 100
#                
#                
#                
#            print "internal_initial_box_num = %s \n" % (internal_initial_box_num)
#            
        
        if all_list_asset == 'y' and  (is_rsdvr_rev3 != 4 and is_rsdvr_rev3 != 5) :
            url = "http://%s/get_boxes?offset=0&limit=100" % (manager)
            #print "url = " + url
            all_home_id = urllib2.urlopen(url)
            xml = all_home_id.read()
            home_id_list.freeDoc()
            home_id_list = libxml2.parseDoc(xml)
            
            
            
            #if total_boxes_size > 100 :
            #    print "Since there are %s boxes, The list
            box_fetch = 100 
            for i in range (1 ,(total_boxes_size / 100) + 2) :
                if i == 1 :
                    current_range = 0
                print "Preparing asset list of boxes from : %s to %s out of %s" % (current_range, box_fetch, total_boxes_size)
                #Checking if PLTV assets are required
                   
                get_boxes_list(manager,home_id_list, "//X/boxes/elem/id", all_list_asset, asset_state,  num_of_boxes, num_assets_to_delete)
                
                url = "http://%s/get_boxes?offset=%s&limit=100" % (manager, box_fetch)
                #print "url = " + url
                all_home_id = urllib2.urlopen(url)
                xml = all_home_id.read()
                home_id_list.freeDoc()
                home_id_list = libxml2.parseDoc(xml)
                
                current_range += 100
                box_fetch += 100
                    
            
            
            home_id_list.freeDoc()    
        #get_boxes_list(manager,home_id_list, "//X/boxes/elem/id", all_list_asset, asset_state, internal_initial_box_num, num_of_boxes, num_assets_to_delete)
        else:
            if is_rsdvr_rev3 != 2 and is_rsdvr_rev3 != 3 and is_rsdvr_rev3 != 4 and is_rsdvr_rev3 != 5:
                del_from_home(manager,initial_box_num,num_of_boxes,num_assets_to_delete,clean_home_ids,rsdvr_rev)
            else:
                del_from_home_v2(manager,initial_box_num,num_of_boxes,num_assets_to_delete,clean_home_ids,rsdvr_rev)
        
        
        
    else : # Delete assets using file
        asset_file = open('asset.list',"r+")
        all_lines = asset_file.readlines()
        for single_lines in all_lines:
            array_delete.append(single_lines)
        asset_file.close    
    #count_lines = len(asset_file.readlines())
    #print "# of lines in file --> %s" %(count_lines)
    
else:  # using rsdvr_asset_list service to retrieve all assets
    
    if reference_apoc_point == 'a' :
        url = "http://%s/rsdvr_asset_list?earliest=%s" %(manager, del_from_time )
        all_assets = urllib2.urlopen(url)
        xml = all_assets.read()            
        all_assets_list = libxml2.parseDoc(xml)
        all_assets_to_del = asset_list_creation_time(manager, all_assets_list, "//X/elem")
    #elif reference_apoc_point == 'b' :
    #    url = "http://%s/rsdvr_asset_list?earliest=0" %(manager)
    #    all_assets = urllib2.urlopen(url)
    #    xml = all_assets.read()
    #    all_assets_list = libxml2.parseDoc(xml)
    #    all_assets_to_del = asset_list_creation_time(manager, all_assets_list, "//X/elem")
        all_assets_list.freeDoc()
    else :
        log.info("APOC reference point configuration is invalid")
    

# Continue with delete : batch + from file 
if ((batch_delete == 'y') and (write_asset_file == 'n')) and is_rsdvr_rev3 != 2:
        index = 0
        temp_url = ""
        if rand == 1:
            create_random_array()
        else:
            pass
        if del_assets_from_file == 'y' :
            asset_file = open('asset.list',"r+")
            all_lines = asset_file.readlines()
            asset_file.close
        
        if (all_list_asset =='y') :
            total_delete_asset = len(array_delete)
        else :
            #total_delete_asset = num_assets_to_delete
            total_delete_asset = total_num_of_asset_to_delete
        if len(array_delete) != 0 :

            if len(array_delete) < batch_size :
                batch_size = len(array_delete)
            if total_delete_asset < batch_size :
                batch_size = total_delete_asset
                
            orig_total_delete_asset = total_delete_asset
            batch_counter = 0
            while ((index < total_delete_asset) and (len(array_delete) > 0) and ((index+1) <= len(array_delete))):
                
                counter = 0
                if (index+batch_size) > len(array_delete) :
                    batch_size = len(array_delete) - (batch_counter  * batch_size)
                elif (index+batch_size) > total_delete_asset:
                    batch_size = total_delete_asset - (batch_counter  * batch_size)

                for i in range(batch_size):                
                    #print "index -->", index, "counter -->", counter, "batch_counter", batch_counter, "array_delete -->", array_delete[index] 
                    temp_url += "&elem%s=%s" % (str(i),array_delete[index].rstrip("\n"))
                    index += 1
                    counter += 1
                if del_assets_from_file == 'y' :
                    del all_lines[0:counter]
                    print all_lines
                        
                    
                    
                        
                #print "temp_url--> %s" %(temp_url)            
                CreateUrl_delete(temp_url, counter)
                temp_url = ""    
                counter = 0
                batch_counter += 1
                #total_delete_asset = total_delete_asset - batch_size
                #print "END-total_delete_asset", total_delete_asset
                if delay_delete_batch > 0 :
                    time.sleep(delay_delete_batch)
                if del_assets_from_file == 'y' :
                    asset_file = open('asset.list',"w")
                    asset_file.writelines(all_lines)
                    asset_file.close
            
        else :
            print "!!! No assets to delete...from Array !!!\n"
            
elif is_rsdvr_rev3 != 2 : #Delete assets from file , NOT using batch)
    if ((batch_delete == 'n') and (write_asset_file == 'n') and (del_assets_from_file == 'y')) :
        asset_file = open('asset.list',"r+")
        all_lines = asset_file.readlines()
        asset_file.close
        delete_xml_doc = None            
        for i in array_delete :
            i = i.strip()
            url = "http://%s/destroy_asset?asset_id=%s&type=%s" % (manager, i,str(soft_delete))#str(urllib.quote_plus(i)).strip())
            print "url = " + url;

            try:
                try:
                    print "Trying to delete asset \"%s\" from file :" %(i)
                    delete_asset = urllib2.urlopen(url)
                    xml_delete = delete_asset.read()
                    delete_xml_doc.freeDoc()
                    delete_xml_doc = libxml2.parseDoc(xml_delete)
                    error_desc = delete_error_parse(manager, delete_xml_doc, "//code")
                    if "Asset deleted successfully by HTTP" in error_desc:
                        print error_desc + "\n"
                        del all_lines[0:1]
                        #print all_lines
                        
                    else :
                        print "Delete failed because : \n\t%s\n" % (i, error_desc)
                except :
                    print "Couldn't delete from file asset : %s\n" % (i)
            finally:
                if delete_xml_doc:
                    delete_xml_doc.freeDoc()
        asset_file = open('asset.list',"w")
        asset_file.writelines(all_lines)
        asset_file.close
        
                


print "The end..."
