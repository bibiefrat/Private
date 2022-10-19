#import sys
from configobj import ConfigObj #to read config file
import libxml2
import os #os function file manipulation
import string
import time
import urllib2
import urllib
import sys
import traceback
#import time
#import urllib
#import logging
#import signal



def delete_assets_from_array(total_assets_array,total_assets_name_array,total_assets_state_array,remove_state,num_assets,name_to_del):  
    #print manager, xpath,num_assetsname_to_del
    # breaking name_to_del into index
    global chunk
    global fsi_asset_id
    delete_array = ()
    delete_name_array = ()
    num_of_delete=0
    if (name_to_del != '' and name_to_del != 'fsi'):
        name_only_to_del = name_to_del[:string.rfind(name_to_del, "_")]
        index_to_del = int(name_to_del[string.rfind(name_to_del, "_")+1:string.rfind(name_to_del, ".")])
        name_delimiter = name_to_del[string.rfind(name_to_del, "."):]
    
    
    
    max_nod_val=0
    theState = []     
#    list = dom.xpathEval(xpath)
    theStates = (toNum(remove_state))
    
        
#    if (name_to_del != ''):   
#        for node in list:
#            #print "*********>>> %d" % int(node.next.next.content[string.rfind(node.next.next.content, "_")+1:string.rfind(node.next.next.content, ".")])
#            if string.rfind(node.next.next.content, "_") != -1 :
#                try:
#                     if max_nod_val <  int(node.next.next.content[string.rfind(node.next.next.content, "_")+1:string.rfind(node.next.next.content, ".")]) :
#                        max_nod_val = int(node.next.next.content[string.rfind(node.next.next.content, "_")+1:string.rfind(node.next.next.content, ".")])
#                except:
#                     ()
    
    if (name_to_del != '' and name_to_del != 'fsi'):   
        for i in total_assets_name_array:
            #print "*********>>> %d" % int(node.next.next.content[string.rfind(node.next.next.content, "_")+1:string.rfind(node.next.next.content, ".")])
            if string.rfind(i, "_") != -1 :
                try:
                     if max_nod_val <  int(i[string.rfind(i, "_")+1:string.rfind(i, ".")]) :
                        max_nod_val = int(i[string.rfind(i, "_")+1:string.rfind(i, ".")])
                except:
                     ()
            time.sleep(0.05)
    
          
    print "********************************************* MAX_NOD_VAL: %d *********************************************" % max_nod_val
    
    ## This is the case you want to delete ALL assets
    counter=0
    if num_assets == -1:
        for j in total_assets_state_array:
            len(total_assets_state_array)
            #print "node = " + str(node)
            #url="http://%s/remove_rsdvr_session?id=%s" % (manager, node.content)
            #print node.next.next.next.netx.content
            for i in theStates:
                if i == int(j):
                    #print "found match " + node.next.next.next.next.content
                    #url= "http://%s/destroy_asset?asset_id=%s&type=0" % (manager, node.content)
            #print "url 2 delete--> %s" % (url)
                    #actual_delete = send_delete(url,node.content,node.next.next.content)
                    delete_array = delete_array + (total_assets_array[counter],)
                    delete_name_array = delete_name_array + (total_assets_name_array[counter],)
                    num_of_delete += 1
            counter = counter +1;        
            time.sleep(0.05)        
                    
    ## This is the case you want to delete a pre-defined number of assets
    elif  num_assets > 0 :
        index=1
        #print "index=%s ; num_assets=%s" % (index,num_assets )
        #print "list=%s" %(list)
        if (name_to_del != '' and name_to_del != 'fsi'):
            for node in range(max_nod_val):
                if index <= num_assets :
    ## If you want to delete  a  pre-defined number of assets and there is a valid asset to delete in the INI file-> the script will delete 
    ## from the first occurrence of the asset name (no matter the index).
                    counter=0             
                    for node1 in total_assets_array:
                        for i in theStates:
                            #print str(i) + "___" + str(node1.next.next.next.next.content) + "------------>>>>>>> " + node1.next.next.content + "-->" + name_to_del
                            if (i == int(total_assets_state_array[counter]) and (total_assets_name_array[counter] == name_to_del) and index <= num_assets):
                                #print node.next.next.content
                                #url= "http://%s/destroy_asset?asset_id=%s&type=0" % (manager, node1.content)
                                #print "url 2 DELETE--> %s" % (url)
                                #actual_delete = send_delete(url,node1.content,node1.next.next.content)
                                delete_array = delete_array + (total_assets_array[counter],)
                                delete_name_array = delete_name_array + (total_assets_name_array[counter],)
                                num_of_delete += 1
                                index += 1
                                break
                            else :
                                #print "didn't find..."
                                continue
                                #print "found match " + node.next.next.next.next.content
                                #url="http://%s/remove_rsdvr_session?id=%s" % (manager, node.content)
                            time.sleep(0.05)
                        counter = counter + 1
                    if index > 1:    
                        index_to_del +=  1 
                        name_to_del = full_name_to_del(name_only_to_del,str(index_to_del),name_delimiter)
                    #if index == num_assets : break
      
        
        
        
        elif (name_to_del == 'fsi'):
            if (fsi_asset_id == ''):            
                for node in range(num_assets):
                    if index <= num_assets :
        ## If you want to delete  a  pre-defined number of assets and there is a valid asset to delete in the INI file-> the script will delete 
        ## from the first occurrence of the asset name (no matter the index).
                        counter=0             
                        for node1 in total_assets_array:
                            for i in theStates:
                                #print str(i) + "___" + str(node1.next.next.next.next.content) + "------------>>>>>>> " + node1.next.next.content + "-->" + name_to_del
                                if (i == int(total_assets_state_array[counter]) and (total_assets_name_array[counter] == '') and index <= num_assets):
                                    #print node.next.next.content
                                    #url= "http://%s/destroy_asset?asset_id=%s&type=0" % (manager, node1.content)
                                    #print "url 2 DELETE--> %s" % (url)
                                    #actual_delete = send_delete(url,node1.content,node1.next.next.content)
                                    delete_array = delete_array + (total_assets_array[counter],)
                                    delete_name_array = delete_name_array + (total_assets_name_array[counter],)
                                    num_of_delete += 1
                                    index += 1
                                    break
                                else :
                                    #print "didn't find..."
                                    continue
                                    #print "found match " + node.next.next.next.next.content
                                    #url="http://%s/remove_rsdvr_session?id=%s" % (manager, node.content)
                                time.sleep(0.05)
                            counter = counter + 1
                        #if index > 1:    
                        #    index_to_del +=  1 
                        #name_to_del = full_name_to_del(name_only_to_del,str(index_to_del),name_delimiter)        
            else:
                for node in range(num_assets):
                    if index <= num_assets :
        ## If you want to delete  a  pre-defined number of assets and there is a valid asset to delete in the INI file-> the script will delete 
        ## from the first occurrence of the asset name (no matter the index).
                        counter=0             
                        for node1 in total_assets_array:
                            for i in theStates:
                                #print str(i) + "___" + str(node1.next.next.next.next.content) + "------------>>>>>>> " + node1.next.next.content + "-->" + name_to_del
                                if (i == int(total_assets_state_array[counter]) and (total_assets_name_array[counter] == '') and index <= num_assets and string.rfind(str(total_assets_array[counter]), str(fsi_asset_id)) != -1):
                                    #print node.next.next.content
                                    #url= "http://%s/destroy_asset?asset_id=%s&type=0" % (manager, node1.content)
                                    #print "url 2 DELETE--> %s" % (url)
                                    #actual_delete = send_delete(url,node1.content,node1.next.next.content)
                                    delete_array = delete_array + (total_assets_array[counter],)
                                    delete_name_array = delete_name_array + (total_assets_name_array[counter],)
                                    num_of_delete += 1
                                    index += 1
                                    break
                                else :
                                    #print "didn't find..."
                                    continue
                                    #print "found match " + node.next.next.next.next.content
                                    #url="http://%s/remove_rsdvr_session?id=%s" % (manager, node.content)
                                time.sleep(0.05)
                            counter = counter + 1
                        #if index > 1:    
                        #    index_to_del +=  1 
                        #name_to_del = full_name_to_del(name_only_to_del,str(index_to_del),name_delimiter)       
        
        
        
        elif (name_to_del == ''):
             if (chunk > num_assets):
                 chunk = num_assets
             else:
                 pass
             counter=0
             for node in total_assets_array:
                 if index <= num_assets :
                  
    ## If you want to delete  a  pre-defined number of assets and there is no valid asset to delete in the INI file-> the script will delete 
    ## from the beginning of the assets list(no matter the index). 
                    for i in theStates:
                        #print str(i) + "___" + str(node.next.next.next.next.content) + "------------>>>>>>> " + node.next.next.content + "-->" + name_to_del
                        if (i == int(total_assets_state_array[counter])):
                            
                            delete_array = delete_array + (total_assets_array[counter],)
                            delete_name_array = delete_name_array + (total_assets_name_array[counter],)
                            #print node.next.next.content
                            #url= "http://%s/destroy_asset?asset_id=%s&type=0" % (manager, node.content)                            
                            #print "url 2 delete--> %s" % (url)
                            #actual_delete = send_delete(url,node.content,node.next.next.content)
                            num_of_delete += 1
                            index += 1
                            break
                        else :
                            #print "didn't find..."
                            continue
                        time.sleep(0.05)
                 counter = counter + 1   
               
                        
    ## If the pre-defined number of assets to delete is '0' and there IS a valid asset to delete in the INI file-> the script will delete 
    ## from the beginning of the assets list all assets with corresponding asset name (no matter the index).           
                        
    elif (num_assets == 0 and name_to_del != '' and name_to_del != 'fsi'):
        for node in range(max_nod_val):
            #print "you've requested to delete all occurances"
            counter=0
            for node1 in total_assets_array:
                for i in theStates:
                    #print "___" + str(node1.next.next.next.next.content) + "------------>>>>>>> " + node1.next.next.content + "-->" + name_to_del

                    if (i == int(total_assets_state_array[counter]) and (total_assets_name_array[counter] == name_to_del)):
                        #url= "http://%s/destroy_asset?asset_id=%s&type=0" % (manager, node1.content)
                        #print "url 2 delete--> %s" % (url)
                        #actual_delete = send_delete(url,node1.content,node1.next.next.content)
                        delete_array = delete_array + (total_assets_array[counter],)
                        delete_name_array = delete_name_array + (total_assets_name_array[counter],)
                        num_of_delete += 1
                    time.sleep(0.05)
                counter = counter + 1
            index_to_del +=  1 
            name_to_del = full_name_to_del(name_only_to_del,str(index_to_del),name_delimiter)
            
    elif (num_assets == 0 and name_to_del == 'fsi'):
#        for node in range(len(total_assets_array)):
            #print "you've requested to delete all occurances"
            if (fsi_asset_id == ''):
                counter=0
                for node1 in total_assets_array:
                    for i in theStates:
                        #print "___" + str(node1.next.next.next.next.content) + "------------>>>>>>> " + node1.next.next.content + "-->" + name_to_del
    
                        if (i == int(total_assets_state_array[counter]) and (total_assets_name_array[counter] == '')):
                            #url= "http://%s/destroy_asset?asset_id=%s&type=0" % (manager, node1.content)
                            #print "url 2 delete--> %s" % (url)
                            #actual_delete = send_delete(url,node1.content,node1.next.next.content)
                            delete_array = delete_array + (total_assets_array[counter],)
                            delete_name_array = delete_name_array + (total_assets_name_array[counter],)
                            num_of_delete += 1
                        time.sleep(0.05)
                    counter = counter + 1
            else:
                counter=0
                for node1 in total_assets_array:
                    for i in theStates:
                        #print "___" + str(node1.next.next.next.next.content) + "------------>>>>>>> " + node1.next.next.content + "-->" + name_to_del
    
                        if (i == int(total_assets_state_array[counter]) and (total_assets_name_array[counter] == '') and string.rfind(str(total_assets_array[counter]), str(fsi_asset_id)) != -1):
                            #url= "http://%s/destroy_asset?asset_id=%s&type=0" % (manager, node1.content)
                            #print "url 2 delete--> %s" % (url)
                            #actual_delete = send_delete(url,node1.content,node1.next.next.content)
                            delete_array = delete_array + (total_assets_array[counter],)
                            delete_name_array = delete_name_array + (total_assets_name_array[counter],)
                            num_of_delete += 1
                        time.sleep(0.05)
                    counter = counter + 1     
             
             
             
    else:
        pass
    delete_the_assets_array(delete_array,delete_name_array)          
    return num_of_delete                
                
                
                
def delete_the_assets_array(delete_array,delete_name_array):
    global chunk
    counter = 0
    total_counter = 0 
    ID_string = ''
    if(chunk > len(delete_array)):
        chunk = len(delete_array)
    elif(chunk < 1):
        chunk = 1
    else:
        pass
    
    print ("delete array:" + str(delete_array) + "\n")
    url = "http://%s/destroy_multiple_asset?size=%s" % (manager,str(chunk))
    ID_string = ''
    names_string = ''
    for i in delete_array:
        if (counter < chunk):
            url += "&elem" + str(counter) + "=" + urllib.quote_plus(i)
            ID_string += i + " " + delete_name_array[total_counter] + "\n"            
            counter += 1
        elif (counter == chunk):
             #print "url:" + url;
             #print (ID_string)
             actual_delete = send_delete(url,ID_string)
             ID_string = ''
             if((len(delete_array) - total_counter) < chunk):
                url =  "http://%s/destroy_multiple_asset?size=%s" % (manager,str(len(delete_array) - total_counter))                
             else:                                            
                url =  "http://%s/destroy_multiple_asset?size=%s" % (manager,str(chunk))            
             url += "&elem0" + "=" + urllib.quote_plus(i)
             ID_string += i + " " + delete_name_array[total_counter] + "\n"
             counter = 1 
        total_counter += 1
        time.sleep(0.05)
    #print "url:" + url;                     
    #print (ID_string)
    actual_delete = send_delete(url,ID_string)




def full_name_to_del(name_only_to_del,index_to_del,name_delimiter):
    #print ("*************FULL NAME***********" + name_only_to_del + "_" + index_to_del  + name_delimiter)
    return (name_only_to_del + "_" + index_to_del  + name_delimiter)


def send_delete(url,node_content):
    p = os.system("wget -q -b -o  /dev/null \"%s\" 1>/dev/null " % (url))
    #try :
    #    response = urllib2.urlopen(url)
     #   xml = response.read()
     #   dom = libxml2.parseDoc(xml)
    #    result = checkByxPath(dom, "/X/code")
        #start_result = result.startswith("0")
   #     if result == '0':
    if p == 0:
        print "Asset/s : ID - name:\n%s was/were deleted successfully." % (node_content)
    else:
        print "Asset/s : ID - name:\n%s could not be deleted .\n Error from manager : %s ." % (node_content)

    #except urllib2.URLError, err:
    #    print "Couldn't open URL for delete .\n url : %s . \n Manager Error : %s ." % (url,err.reason)
  

def checkByxPath(dom, xpath):   
                
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content
    return r


def toNum(list):
    
    num_list = []
    for i in list:
        num_list.append(int(i)) 
    #print num_list    
    return num_list

def from_list_to_array(num_of_assets):
    global manager
    total_assets_array = ()
    total_assets_name_array = ()
    total_assets_state_array = ()
    global num_of_delete
    global name_to_del
    global remove_all_assets
    global asset_state_to_remove
    assets_list=None
    total_remaining = num_of_assets
    offset = 0       
    while ( total_remaining > 0):
        #we set num to get =100 because this is configured in the manager ini file              
        url = "http://%s/get_all_assets?asset_type=0&offset=%s&num_to_get=100" % (manager,offset)
        #print "url = " + url
        all_assets = urllib2.urlopen(url)
        xml = all_assets.read()
        assets_list = libxml2.parseDoc(xml)
        list_id = assets_list.xpathEval("//X/assets/elem/id")
        list_name =  assets_list.xpathEval("//X/assets/elem/name")
        list_state = assets_list.xpathEval("//X/assets/elem/state")
        
        for node in list_id:
            total_assets_array = total_assets_array + (node.content.strip(),)
        for node in list_name:
            total_assets_name_array = total_assets_name_array + (node.content.strip(),)
        for node in list_state:
            total_assets_state_array = total_assets_state_array + (node.content.strip(),)      
        total_remaining = int(total_remaining) - 100
        offset = int(offset) + 100
        time.sleep(0.05)
        assets_list.freeDoc()
#    if remove_all_assets == 'y':
#    delete_assets(manager, assets_list, "//X/info/elem/recording/external_id", 0)    
#        print "<<<<<<<<<<<<<<<<<<<<<<<<<< Total Num of Deletion: %d >>>>>>>>>>>>>>>>>>>>>>>>>>> \n" % delete_assets_from_array(total_assets_array,total_assets_name_array,total_assets_state_array,asset_state_to_remove, -1, name_to_del)
             
#    else :
   #delete_assets(manager, assets_list, "//X/info/elem/recording/external_id", num_of_delete)
    print "<<<<<<<<<<<<<<<<<<<<<<<<<< Total Num of Deletion: %d >>>>>>>>>>>>>>>>>>>>>>>>>>> \n" % delete_assets_from_array(total_assets_array,total_assets_name_array,total_assets_state_array,asset_state_to_remove, num_of_delete, name_to_del)
        
    #print total_assets_array
    #print len(total_assets_array)
    #print total_assets_name_array
    #print total_assets_state_array
    
    
def delete_all(num_of_assets):
    global manager
    total_assets_array = ()
    total_assets_name_array = ()
    total_assets_state_array = ()
    global num_of_delete
    global name_to_del
    global remove_all_assets
    global asset_state_to_remove
    counter=0
    offset = 0
    ID_string = ''
    assets_list = None
    url = "http://%s/get_all_assets?asset_type=0&offset=0&num_to_get=10000" % (manager)
    #print "url = " + url
    all_assets = urllib2.urlopen(url)
    xml = all_assets.read()
    assets_list = libxml2.parseDoc(xml)
    num_of_assets = int(checkByxPath(assets_list , "//X/total_assets"))
    
    print "TOTAL REMAINING BEFORE: " +  str(num_of_assets)      
    while (num_of_assets > 0):
        #we set num to get =100 because this is configured in the manager ini file              
        url = "http://%s/get_all_assets?asset_type=0&offset=%s&num_to_get=100" % (manager,offset)
        #print "url = " + url
        all_assets = urllib2.urlopen(url)
        xml = all_assets.read()
        assets_list.freeDoc()
        assets_list = libxml2.parseDoc(xml)
        list_id = assets_list.xpathEval("//X/assets/elem/id")
        list_name =  assets_list.xpathEval("//X/assets/elem/name")
        list_state = assets_list.xpathEval("//X/assets/elem/state")
        if num_of_assets > 100:
            url =  "http://%s/destroy_multiple_asset?size=%s" % (manager,100)
            for i in list_id:
                url += "&elem" + str(counter) + "=" + urllib.quote_plus(str(i.content.strip()))
                ID_string += str(i.content.strip()) + " " + list_name[counter].content.strip() + "\n" 
                counter+=1                        
            send_delete(url,ID_string)
        else:
            url =  "http://%s/destroy_multiple_asset?size=%s" % (manager,num_of_assets)
            for i in list_id:
                url += "&elem" + str(counter) + "=" + urllib.quote_plus(str(i.content.strip()))
                ID_string += str(i.content.strip()) + " " +  list_name[counter].content.strip() + "\n" 
                counter+=1
            send_delete(url,ID_string)
        counter=0
        ID_string=''
        url=''
        url = "http://%s/get_all_assets?asset_type=0&offset=0&num_to_get=100" % (manager)
        #print "url = " + url
        all_assets = urllib2.urlopen(url)
        xml = all_assets.read()
        assets_list.freeDoc()
        assets_list = libxml2.parseDoc(xml)
        num_of_assets = int(checkByxPath(assets_list , "//X/total_assets"))        
        print "TOTAL REMAINING DURING: " +  str(num_of_assets)        
        offset=0
        time.sleep(0.3)
    print "TOTAL REMAINING AFTER: " +  str(num_of_assets)    
        

def delete_asset_by_db(num_of_assets):
    global chunk
    global fsi_asset_id
    global name_to_del
    global num_of_delete
    global db_addr
    global num_of_delete
    global chunk
    global edges
    global is_demote
    try:       
        x = os.path.exists("db.tmp")
        if x == True :
            print "Removing old rsdvr_asset.list file...\n"
            z = os.remove("db.tmp")
        else:
            print "File rsdvr_asset.list does not exist"

    except:
        pass
    
    db_file = open("db.tmp","w")
    
    #if name_to_del != '':
    if name_to_del != '':    
        name_only_to_del = name_to_del[:string.rfind(name_to_del, "_")]
    else:
        name_only_to_del = ''
    x = '''expect -c "set timeout -1;
         spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \\\\\\"select count\(*\) from asset where active='1' and meta_name like '%%%s%%'\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
         match_max 100000;
         expect *password:*;
         send -- F@brix\\r;
         interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows > db.tmp'''  % (str(db_addr),str(name_only_to_del))
    try:
         print x
         os.system(x)
    except:
        traceback.print_exc(file=sys.stdout)
    db_file.close()
    db_file = open("db.tmp","r")
    num_of_asset_to_del = str(db_file.readline()).strip()
    db_file.close()
    if num_of_delete == 0:
        pass
    else:
        num_of_asset_to_del = num_of_delete
    #z = os.remove("db.tmp")                 
    db_file = open("db.tmp","w")
    total_offset = 0
    while num_of_asset_to_del > 0:
        #if num_of_asset_to_del < 1000:
        if num_of_asset_to_del < int(chunk):
            offset = num_of_asset_to_del
        else:
            #offset = 1000
            offset = int(chunk)           
        #total_offset = total_offset + offset
#        x = '''expect -c "set timeout -1;
#             spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \\\\\\"select external_id from asset where active='1' and meta_name like '%%%s%%' limit %s  offset %s\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
#             match_max 100000;
#             expect *password:*;
#             send -- fabrix\\r;
#             interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows > db.tmp'''  % (str(db_addr),str(name_only_to_del),str(offset),str(total_offset))
             
        x = '''expect -c "set timeout -1;
             spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e \\\\\\"select external_id,data_id from asset where active='1' and meta_name like '%%%s%%' limit %s  offset %s\\\\\\" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
             match_max 100000;
             expect *password:*;
             send -- F@brix\\r;
             interact;" | tail -n +7  | grep -v rows  | sed '/^\s*$/d'  > db.tmp'''  % (str(db_addr),str(name_only_to_del),str(offset),str(total_offset))
                         
             
             
        try:
             print x
             os.system(x)
        except:
            traceback.print_exc(file=sys.stdout)
            pass
        
        num_of_asset_to_del = int(num_of_asset_to_del) - int(offset)
        db_file.close()
        #z = os.remove("db.tmp")                 
        db_file = open("db.tmp","r")
        
        ID_string =''
        if (is_demote==0):
            counter = 0
            mydata = []
            url =  "http://%s/destroy_multiple_asset?size=%s" % (manager,offset)
            mydata.insert(0,('size',str(offset)))
            for i in range(offset):
                line = str(db_file.readline()).strip()
                asset_id = line[:line.find(" ")].strip()
                url += "&elem" + str(counter) + "=" + urllib.quote_plus(str(asset_id))
                ID_string += str(asset_id) + " " + "\n"
                counter+=1
                mydata.insert(i + 1,('elem' + str(i),str(asset_id)))               
            #print url                        
            #send_delete(url,ID_string)
            mydata=urllib.urlencode(mydata)
            path="http://%s/destroy_multiple_asset" % (manager)
            req=urllib2.Request(path, mydata)
            req.add_header("Content-type", "application/x-www-form-urlencoded")
            page=urllib2.urlopen(req).read()
            print "Delete by the following URL: \n" + mydata
        elif is_demote == 1:
           try:
                try:
                    Region_ID_url = "http://%s/get_topology?X=0" % (manager)
                    Region_result = urllib2.urlopen(Region_ID_url)
                    xml_Region = Region_result.read()
                    parse_region = libxml2.parseDoc(xml_Region)
                    num_of_edges = checkByxPath(parse_region, "//X/online/regions/elem/edges/size")
                    num_of_edges_as_ingest_points =  checkNumIngestPoints(parse_region)
                except:
                    print "Error while trying to get Region ID"
                    print "url --> " + str(Region_ID_url)
                    pass
           finally:
                if parse_region:
                    parse_region.freeDoc()
            
           counter = 0
           for i in range(offset):
              #asset_id = str(db_file.readline()).strip()
              line =  str(db_file.readline()).strip()
              asset_id = line[line.rfind(" "):].strip()
              for j in range(len(edges)):
                  url = "http://%s/demote_asset?asset_id=%s&edge_id=%s" % (str(manager),urllib.quote_plus(str(asset_id)),str(edges[j]))
                  print "Demoting: " + url
                  urllib2.urlopen(url)
              counter+=1
        total_offset = total_offset + offset           
        counter=0
        ID_string=''
        db_file.close()
        #z = os.remove("db.tmp")                 
        
        #db_file.close()
        z = os.remove("db.tmp")
    
 
def checkNumIngestPoints(url):
    #global edges_as_ingest_point
    #global params
    global manager_ver
    version_num = manager_ver.split(".")
    counter = 0
    edge_is_ingest_point_parse = None
    if ((version_num[0] == 2) and (version_num[1] == 8) and (version_num[3] >= 4)) or (version_num[0] > 2):
        try:
            try:
                edge_is_ingest_point_url = "http://%s/vs_group/get_groups?X=0" % (str(manager))
                edge_is_ingest_point_open_url=urllib2.urlopen(edge_is_ingest_point_url)
                edge_is_ingest_point_response = edge_is_ingest_point_open_url.read()
                edge_is_ingest_point_parse = libxml2.parseDoc(edge_is_ingest_point_response)
                list = edge_is_ingest_point_parse.xpathEval("*//props")
                counter = 0
                for i in list:
                    if int(i.xpathEval('ingest')[0].content) == 1:
                        if i.xpathEval('replication') != []:
                            counter += int(i.xpathEval('replication')[0].content)
                        else:
                            counter += 1
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
                    edge_is_ingest_point_url = "http://%s/get_edge_props?X=%s" % (manager,edge_id)
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


def addByxPath(dom, xpath):              
    list = dom.xpathEval(xpath)
    for url in list:
        o = url.content
       
    return o
# ------------------------------------------------------
# Main

# Getting current folder location
path = "../"
#path = os.getcwd()

edges = []

# Reading configuration file
config = ConfigObj(path+'/conf/config.ini')
manager_parse_ver = None
assets_list = None
manager = config['Configuration']['manager']
remove_all_assets = config['Configuration']['all_assets']
num_of_delete = int(config['Configuration']['size_remove_assets'])
name_to_del = config['Configuration']['start_name']
asset_state_to_remove = config['Configuration']['asset_state_to_remove']
# Getting the manager version
manager_ver_url = "http://%s/get_versions?X=0" % (manager)
manager_ver_open_url=urllib2.urlopen(manager_ver_url)
manager_ver_response = manager_ver_open_url.read()
manager_parse_ver = libxml2.parseDoc(manager_ver_response)
manager_ver = checkByxPath(manager_parse_ver, "//X/mngr_ver")
chunk = int(config['Configuration']['chunk'])
fsi_asset_id = config['Configuration']['fsi_asset_id']
use_db = int(config['Configuration']['use_db'])
db_addr = str(config['Configuration']['db_addr'])
edge = config['Configuration']['edge']
is_demote = int(config['Configuration']['is_demote'])
manager_parse_ver.freeDoc()
#
#print "manager version -->" + str(manager_ver):

edges = edge.split(";")

try:
        try :
            manager_ver_url = "http://%s/get_versions?X=0" % (manager)
            manager_ver_open_url=urllib2.urlopen(manager_ver_url)
            manager_ver_response = manager_ver_open_url.read()
            manager_parse_ver = libxml2.parseDoc(manager_ver_response)
            manager_ver = addByxPath(manager_parse_ver, "/X/mngr_ver")
            #CM_ver = addByxPath(manager_parse_ver, "//X/cm_ver")
            print "manager version -->" + str(manager_ver)
        except Exception, err:
            traceback.print_exc(file=sys.stdout)
            print "Cant get manager version!!!"
            sys.exit()
        
finally:
       if manager_parse_ver:
           manager_parse_ver.freeDoc()



# Opening the XML of the assets list
#url = "http://%s/get_assets?max_items=10000&offset=0" % (manager)
url = "http://%s/get_all_assets?asset_type=0&offset=0&num_to_get=10000" % (manager)
#print "url = " + url
all_assets = urllib2.urlopen(url)
xml = all_assets.read()
assets_list = libxml2.parseDoc(xml)
num_of_assets = checkByxPath(assets_list , "//X/total_assets")
assets_list.freeDoc()
if remove_all_assets != 'y' and use_db == 0:
    from_list_to_array(num_of_assets)
elif remove_all_assets == 'y':
    delete_all(num_of_assets)
elif remove_all_assets != 'y' and use_db == 1:
    delete_asset_by_db(num_of_assets)

time.sleep(5)

os.system("find %s -name \'destroy_multiple*\'  | xargs rm" % (path + "/src"))
print "\n\nFinished deleting asset list"


