import urllib2
from configobj import ConfigObj
import os
import sys
import libxml2


def checkByxPath(dom, xpath):   
                
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content

    return r

def getElemVal(xml, location, name):
    start_pos = xml.find('>', xml.find(name, location)) + 1
    end_pos = xml.find('</' + name, start_pos)
    return xml[start_pos:end_pos].strip()

# ------------------------------------------------------
# Main

# Getting current folder location
path = "../"

# Reading configuration file
config = ConfigObj(path+'conf/config.ini')

asset_list_path = config['Configuration']['recording_list_path']
manager = config['Configuration']['manager']
all_list_asset = (config['Configuration']['all_list_asset'] == 'y')
size_list_assets = int(config['Configuration']['size_list_assets'])
get_recording = (config['Configuration']['get_recording'] == 'y')
get_ready = (config['Configuration']['get_ready'] == 'y')

try :
# Deleting current recording.list file
    z = os.remove(asset_list_path)
except :
    pass

if not get_ready and not get_recording:
    print "Need to get at least one of recording assets and ready recorded assets"
    sys.exit(-1)


url = "http://" + manager + "/get_recordings?max_items=1&offset=0"
all_assets = urllib2.urlopen(url)
xml = all_assets.read()
recording_list = libxml2.parseDoc(xml)
all_assets.close()
num_of_recordings = checkByxPath(recording_list , "//X/total_recordings")
recording_list.freeDoc()

current_range=0
id_asset_list = []
for i in range (1 ,(int(num_of_recordings) / 100) + 2) :

    # Opening the XML of the asset list
    url = "http://" + manager + "/get_recordings?max_items=100&offset=%s" % (str(current_range))
    all_assets = urllib2.urlopen(url)
    xml = all_assets.read()
    all_assets.close()
    #print xml
    
    
    
    counter = 0
    index = xml.find ('<elem')
    
    while index != -1:
        external_id = getElemVal(xml, index, "external_id")
        state = getElemVal(xml, index, "state")
        # Either we wish to get recording assets and this asset is recording,
        # or we wish to get ready assets and this asset is either ready or distributing
        if get_recording and state == '0' or get_ready and (state == '1' or state == '2'):
            id_asset_list.append(external_id)
            counter += 1
            if not all_list_asset and counter == size_list_assets:
                break
        index = xml.find('<elem', index + 1)
    current_range += 100

asset_file = open(asset_list_path, 'w')
for external_id in id_asset_list:
    asset_file.write(external_id)
    asset_file.write(" 0 -1\n")
asset_file.close()

print "Finished creating recording list file"

