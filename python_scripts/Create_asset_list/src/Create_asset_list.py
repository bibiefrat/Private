#import sys
#import string
#import time
import urllib2
#import urllib
import libxml2
#import logging
from configobj import ConfigObj
#import signal
import os
import time

assetElements = {
                 'state' : "2",
                 'startPlay' : "0",
                 'endPlay' : "-1",
                 'type' : "1"
                 }


def get_asset_by_id(dom, xpath,id_asset_list):  
    global all_list_asset
    global size_list_assets
    global start_asset_name
    global fsi_id
    
    index = 0
    #print "[get_asset_by_id] checking for id: " + asset_id      
    list = dom.xpathEval(xpath)
    
    for node in list:
        #print "node = " + str(node)       
        if node.content == assetElements['state']:
            
            #print "--------------"
            #oParent = node.parent
            
            # for each state we found we are getting its "assetName" and 
            # its "assetId".
            assetName = node.prev.prev.content
            assetId = None
            try:
                # Try getting the asset id from the <full_path> element
                assetId = node.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.next.content
            except:
                pass
            if assetId is None or not assetId.startswith("/"):
                # If failed getting the asset id from the <full_path> element, get it from the regular location
                assetId = node.prev.prev.prev.prev.content
            # script will refer only to assets whose ID is according to Shaw format
            if (Shaw_format == 1):
                if assetId.startswith("/"):
                    if all_list_asset == 'y':
                        id_asset_list.append(assetId)                       
                    else:
                        if index+1 <= size_list_assets and str(assetId).find(fsi_id) >= 0:
                            id_asset_list.append(assetId)
                            index += 1
           # script will refer only to assets whose ID is NOT according to Shaw format
            elif (Shaw_format == 0):
                if not assetId.startswith("/"):
                    if start_asset_name == '':
                        if all_list_asset == 'y':
                            id_asset_list.append(assetId)                            
                        else:
                            if index+1 <= int(size_list_assets):
                                id_asset_list.append(assetId)
                                index += 1                
                    else:                
                        if assetName.startswith(start_asset_name):
                            if all_list_asset == 'y':
                                id_asset_list.append(assetId)
                            else:
                                if index+1 <= size_list_assets:
                                    id_asset_list.append(assetId)
                                    index += 1
#            elif (Shaw_format == 2):
#            
#                if start_asset_name == '':
#                    if all_list_asset == 'y':
#                        id_asset_list.append(assetId)
#                    else:
#                        if index+1 <= int(size_list_assets):
#                            id_asset_list.append(assetId)
#                            index += 1                
#                else:                
#                    if assetName.startswith(start_asset_name):
#                        if all_list_asset == 'y':
#                            id_asset_list.append(assetId)
#                        else:
#                            if index+1 <= size_list_assets:
#                                id_asset_list.append(assetId)
#                                index += 1                
#            
            elif (Shaw_format == 2):
            
                if all_list_asset == 'y':                    
                        id_asset_list.append(assetId)                         
                else:   
                    if index+1 <= size_list_assets:
                        if assetId.startswith("/"):
                            if fsi_id == '':
                              id_asset_list.append(assetId)
                            elif str(assetId).find(fsi_id) >= 0:
                              id_asset_list.append(assetId)
                            index += 1
                        else:
                            if start_asset_name == '':
                              id_asset_list.append(assetId)
                            elif assetName.startswith(start_asset_name):
                              id_asset_list.append(assetId)
                            index += 1       
        else:
		if( node.content.startswith("LIVE$")):
			assetId=node.content[2:]
		
			assetId = "/"+assetId.split("$")[1] + "/" + assetId.split("$")[0]
			print assetId
                	if all_list_asset == 'y':
                        	id_asset_list.append(assetId)
                	else:
	                    	if index+1 <= size_list_assets:
        	                	id_asset_list.append(assetId)
                	        	index += 1
                             
                    
     
            
            
    #print "asset_id_list = " + str(id_asset_list)
    return id_asset_list


def get_ad_details(dom, xpath):
    
    list = dom.xpathEval(xpath)

    for node in list:
        #print "node = " + str(node)
        # founding the add (which type=1)
        if node.content == assetElements['type']:
            #verifing that the state of the asset is "1" --> "Ready"
            if node.prev.prev.prev.prev.prev.prev.content == assetElements['state']:           
                # founding "assetName" & "assetId" of the ad 
                ad_Name = node.prev.prev.prev.prev.prev.prev.prev.prev.content
                ad_Id = node.prev.prev.prev.prev.prev.prev.prev.prev.prev.prev.content
                #print "ad name = " + ad_Name
                #print "ad id = " + ad_Id
    
    return (ad_Name,ad_Id)


def create_file(list_asset_id, ad_name, ad_id):
    global use_splice
    global num_splices
    global splice_time_gap
    global splice_play_time 

    
    asset_file = open("../asset.list", "a")
    num_asset = int(len(list_asset_id))
    
    if use_splice == "y":
        
        for i in range(num_asset):
            startPlay = 0
            endPlay = splice_time_gap
            
            asset_file.write("%s %s %s:" %(list_asset_id[i], startPlay, endPlay))
        
            for j in range(num_splices):
                startPlay = endPlay
                endPlay += splice_time_gap
                if (j+1) < num_splices:
                    asset_file.write("%s %s %s:%s %s %s:" %(ad_id, 0, splice_play_time, list_asset_id[i], startPlay, endPlay))
                else :
                    asset_file.write("%s %s %s:%s %s %s\n" %(ad_id, 0, splice_play_time, list_asset_id[i], startPlay, assetElements['endPlay']))
    
        
    else:
        for i in range(num_asset):
            if (i+1) < num_asset:
                asset_file.write("%s %s %s\n" %(list_asset_id[i], assetElements['startPlay'], assetElements['endPlay']))
            else:
                asset_file.write("%s %s %s" %(list_asset_id[i], assetElements['startPlay'], assetElements['endPlay']))
    asset_file.close()
     
def checkByxPath(dom, xpath):   
                
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content

    return r

# ------------------------------------------------------
# Main

# Getting current folder location
#path = os.getcwd()
path = "../"
# Reading configuration file
config = ConfigObj(path+'conf/config.ini')
manager_parse_ver = None
assets_list =None
asset_list_path = config['Configuration']['asset_list_path']
manager = config['Configuration']['manager']
all_list_asset = config['Configuration']['all_list_asset']
size_list_assets = int(config['Configuration']['size_list_assets'])
start_asset_name = config['Configuration']['start_asset_name']
fsi_id = config['Configuration']['fsi_id']
use_splice = config['Configuration']['use_splice']
use_specific_ad_id = config['Configuration']['use_specific_ad_id']
ad_specific_id = config['Configuration']['ad_specific_id']
Shaw_format = int(config['Configuration']['Shaw_format'])
num_splices = int(config['Configuration']['num_splices'])
splice_time_gap = int(config['Configuration']['splice_time_gap'])
splice_play_time = int(config['Configuration']['splice_play_time'])
use_rsdvr=int(config['Configuration']['get_rsdvr_assets'])

try :
# Deleting current asset.list file
    z = os.remove(asset_list_path)
except :
    pass

# Getting the manager version
manager_ver_url = "http://%s/get_versions?X=0" % (manager)
manager_ver_open_url=urllib2.urlopen(manager_ver_url)
manager_ver_response = manager_ver_open_url.read()
manager_parse_ver = libxml2.parseDoc(manager_ver_response)
manager_ver = checkByxPath(manager_parse_ver, "//X/mngr_ver")
manager_parse_ver.freeDoc()
#print "manager version -->" + str(manager_ver)


# Opening the XML of the asset list
if (manager_ver == "2.0.0.1") or (manager_ver == "2.0.0.2") or (manager_ver == "2.0.0.3") or (manager_ver == "2.0.0.4") :
    url = "http://" + manager + "/get_all_assets?X=0"
else:
    #url = "http://" + manager + "/get_all_assets?asset_type=0&last_id=0&num_to_get=-1"
    url = "http://" + manager + "/get_all_assets?asset_type=0&offset=0&num_to_get=-1&descending=0"
if(use_rsdvr):
    url="http://" + manager + "/rsdvr_asset_list?earliest=0"

#print "url = " + url
all_assets = urllib2.urlopen(url)
xml = all_assets.read()
assets_list = libxml2.parseDoc(xml)
if(use_rsdvr):
    num_of_assets= checkByxPath(assets_list , "//X/size")
else:
    num_of_assets= checkByxPath(assets_list , "//X/total_assets")

#print "asset-list -->" + str(assets_list)

# Parsing the assets list according to the state=Ready
id_asset_list = []
total_remaining = num_of_assets
offset = 0       
while ( total_remaining > 0):
    if (manager_ver == "2.0.0.1") or (manager_ver == "2.0.0.2") or (manager_ver == "2.0.0.3") or (manager_ver == "2.0.0.4") :
        url = "http://" + manager + "/get_all_assets?X=0"
    else:
    #url = "http://" + manager + "/get_all_assets?asset_type=0&last_id=0&num_to_get=-1"
        url = "http://" + manager + "/get_all_assets?asset_type=0&offset=" + str(offset) + "&num_to_get=100&descending=0"
    if(use_rsdvr):
        url="http://" + manager + "/rsdvr_asset_list?earliest=0"


    all_assets = urllib2.urlopen(url)
    xml = all_assets.read()
  #  print xml
    assets_list = libxml2.parseDoc(xml)
    
    if (manager_ver == "2.0.0.1") or (manager_ver == "2.0.0.2") or (manager_ver == "2.0.0.3") or (manager_ver == "2.0.0.4") :
        list_asset_id = get_asset_by_id(assets_list, "X/elem/state",id_asset_list)
    else :
	if(use_rsdvr):
	     list_asset_id = get_asset_by_id(assets_list, "X/elem",id_asset_list)
	     break
	else:

             list_asset_id = get_asset_by_id(assets_list, "X/assets/elem/state",id_asset_list)
    
    total_remaining = int(total_remaining) - 100
    offset = int(offset) + 100
    print "<<<<<<<<<<<>>>>>>>>>>>" + str(offset) + " total temain" + str(total_remaining)
    
    
# Finding the name & ID of the ad asset
if use_specific_ad_id == 'y':
    ad_details = ['asset_name', ad_specific_id]
else:
    ad_details = get_ad_details(assets_list,"X/elem/type")


# Creating the asset file
create_file(list_asset_id, ad_details[0], ad_details[1])



print "Finished creating asset list file"
assets_list.freeDoc()
