#import sys
import string
#import time
import urllib2
import urllib
import libxml2
import logging
from configobj import ConfigObj
import signal
import os
import time
import ftplib


class progressBar:
    def __init__(self, minValue = 0, maxValue = 10, totalWidth=12):
        self.progBar = "[]"   # This holds the progress bar string
        self.min = minValue
        self.max = maxValue
        self.span = maxValue - minValue
        self.width = totalWidth
        self.amount = 0       # When amount == max, we are 100% done 
        self.updateAmount(0)  # Build progress bar string

    def updateAmount(self, newAmount = 0):
        if newAmount < self.min: newAmount = self.min
        if newAmount > self.max: newAmount = self.max
        self.amount = newAmount

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self.amount - self.min)
        percentDone = (diffFromMin / float(self.span)) * 100.0
        percentDone = round(percentDone)
        percentDone = int(percentDone)

        # Figure out how many hash bars the percentage should be
        allFull = self.width - 2
        numHashes = (percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        # build a progress bar with hashes and spaces
        self.progBar = "[" + '#'*numHashes + ' '*(allFull-numHashes) + "]"

        # figure out where to put the percentage, roughly centered
        percentPlace = (len(self.progBar) / 2) - len(str(percentDone)) 
        percentString = str(percentDone) + "%"

        # slice the percentage into the bar
        self.progBar = self.progBar[0:percentPlace] + percentString + self.progBar[percentPlace+len(percentString):]

    def __str__(self):
        return str(self.progBar)


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





assetElements = {
                 'state' : "2",
                 'startPlay' : "0",
                 'endPlay' : "-1",
                 'type' : "1"
                 }


def get_asset_by_id(dom, xpath,id_asset_list, name_asset_list, checksum_asset_list ):  
    
    
    index = 0
    #print "[get_asset_by_id] checking for id: " + asset_id      
    list = dom.xpathEval(xpath)
    
    for node in list:

        #print "node = " + str(node)
        if node.content == assetElements['state']:
            
            assetName = node.prev.prev.content
            assetId = node.prev.prev.prev.prev.content
            
            url = "http://%s/get_asset_properties?external_id=%s&internal_id=0" % (manager, urllib.quote_plus(assetId))
            #print url
            asset_info = urllib2.urlopen(url)
            xml = asset_info.read()
            asset_list = libxml2.parseDoc(xml)
            
            if all_assets_checksum == 'y' :    
                try : 
                    asset_checksum = checkByxPath(asset_list, "/X/ext/checksum")
                    id_asset_list.append(assetId)
                    name_asset_list.append(assetName)
                    checksum_asset_list.append(asset_checksum)
                    #print "id_asset_list-->", id_asset_list
                except : 
                    pass

            else : 
                if ((name_asset != '') and (all_assets_checksum == 'n')) :
                    if (assetName.find(name_asset,0) != -1 ) :
                        try : 
                            asset_checksum = checkByxPath(asset_list, "/X/ext/checksum")
                            id_asset_list.append(assetId)
                            name_asset_list.append(assetName)
                            checksum_asset_list.append(asset_checksum)
                        except : 
                            pass
                                  
                

    return id_asset_list, name_asset_list, checksum_asset_list


def create_file( id_asset_list, name_asset_list, checksum_asset_list ) :
      
    asset_file = open("../conf/checksum_output.list", "w")
    
    
    
    if ( len(id_asset_list) == len(name_asset_list) == len(checksum_asset_list) ):
        for i in range(len(id_asset_list)): 
            if i+1 < len(id_asset_list) :
                asset_file.write("%s %s %s\n" % (str(id_asset_list[i]), str(name_asset_list[i]), str(checksum_asset_list[i])))
            else : # writing last line
                asset_file.write("%s %s %s" % (str(id_asset_list[i]), str(name_asset_list[i]), str(checksum_asset_list[i])))
         
    

    asset_file.close()
    

def gettext(ftp, filename, outfile=None):
    # fetch a text file
    if outfile is None:
        outfile = sys.stdout
    # use a lambda to add newlines to the lines read from the server
    ftp.retrlines("RETR " + filename, lambda s, w=outfile.write: w(s+"\n"))

def getbinary(ftp, filename):
    # fetch a binary file
    f = file(filename, "w")
    ftp.retrbinary("RETR " + filename, f.write)
    f.close ()






def ftp_get (ftp_server, asset_id):
    
    ftp = ftplib.FTP("%s" % (ftp_server))
    ftp.login("anonymous","")
    #ftp.login("anonymous", "fabrix")

    #gettext(ftp, "README")
    ftp.cwd(".shared")
    getbinary(ftp, "%s" % (asset_id))
    os.system("md5sum %s" % (asset_id))


def checkByxPath(dom, xpath):   
                
    list = dom.xpathEval(xpath)
    for url in list:
        r = url.content
        #print "r--> ", r

    return r

# ------------------------------------------------------
# Main

# Getting current folder location
#path = os.getcwd()
path = "../"
# Reading configuration file
config = ConfigObj(path+'/conf/config.ini')

manager = config['Configuration']['manager']
ftp_file_location = config['Configuration']['ftp_file_location']
checksum_file_location = config['Configuration']['checksum_file_location']
all_assets_checksum = config['Configuration']['all_assets_checksum']
name_asset = config['Configuration']['name_asset']
log_file = config['Configuration']['log_file']
log_level = string.upper(config['Configuration']['desired_log_level'])


try:  
    x = os.path.exists("../conf/checksum_output.list")
    if x == True :
        print "Removing old checksum_output.list file...\n"
        z = os.remove(asset_list_path)
    else:
        print "File checksum_output.list does not exist"

except:
    pass




#try :
# Deleting current asset.list file
#    z = os.remove(checksum_file_location)
#except :
#    pass


defineLogger()
log = logging.getLogger('Main')

# Getting the manager version
manager_ver_url = "http://%s/get_versions?X=0" % (manager)
manager_ver_open_url=urllib2.urlopen(manager_ver_url)
manager_ver_response = manager_ver_open_url.read()
manager_parse_ver = libxml2.parseDoc(manager_ver_response)
manager_ver = checkByxPath(manager_parse_ver, "//X/mngr_ver")
#
#print "manager version -->" + str(manager_ver)


# Opening the XML of the asset list 300

url = "http://%s/get_all_assets?asset_type=0&offset=0&num_to_get=-1&descending=0" % (manager)

#print "url = " + url
all_assets = urllib2.urlopen(url)
xml = all_assets.read()
assets_list = libxml2.parseDoc(xml)
num_of_assets = checkByxPath(assets_list , "//X/total_assets")
#print "asset-list -->" + str(assets_list)

# Parsing the assets list according to the state=Ready
id_asset_list = []
name_asset_list = []
checksum_asset_list = [] 
total_remaining = num_of_assets
print "total assets --> %s" %(total_remaining)
offset = 0  

asset_percent = int ( 100 / ((int(total_remaining) / 100)+1) )
asset_percent_temp = asset_percent
print "Starting to process %s files that are ingested in the system \n" % (num_of_assets)     
while ( total_remaining > 0 ):
    prog = progressBar(0, 100, 77)
    #print "total remaining -->", total_remaining
    prog.updateAmount(asset_percent)
    print prog, "\r",
    #time.sleep(.05)
    url = "http://%s/get_all_assets?asset_type=0&offset=%s&num_to_get=-1&descending=0" % (manager,str(offset))

    all_assets = urllib2.urlopen(url)
    xml = all_assets.read()
    assets_list = libxml2.parseDoc(xml)
    list_asset_id = get_asset_by_id(assets_list, "X/assets/elem/state", id_asset_list, name_asset_list, checksum_asset_list )
    
    
    total_remaining = int(total_remaining) - 100
    if total_remaining < 0 :
        total_remaining = 0
    
    offset = int(offset) + 100
    #if total_remaining > 0 :
        
        #print "Assets processed so far : %s .  Total remaining assets = %s . " % (str(offset), str(total_remaining))

    asset_percent += asset_percent_temp

# Creating the checksum file 
length_assets_array = len(list_asset_id[0])
#print "There are total of %s assets that were tested according to the criteria. " % (length_assets_array)
id_asset_list = list_asset_id[0]
name_asset_list = list_asset_id[1]
checksum_asset_list = list_asset_id[2]

# Creating the asset file
create_file(id_asset_list, name_asset_list, checksum_asset_list)


#Comparing the checksums 

# Opening files :

ftp_asset_file = open ("../conf/ftp_assets.list", "r")
checksum_asset_file = open ("../conf/checksum_output.list", "r")


ftp_all_lines = ftp_asset_file.readlines()
num_asset_lines = len(ftp_all_lines)
checksum_all_lines = checksum_asset_file.readlines()
print "\nTotal assets in FTP file to be compared : %s . " % (num_asset_lines)
asset_compared = 0
ok_counter = 0
bad_counter = 0
#print num_asset_lines     
for ftp_single_lines in ftp_all_lines:
    ftp_inner_data = str(ftp_single_lines).split(" ")
    if ((name_asset != '') and (all_assets_checksum == 'n')) :
        if (ftp_inner_data[1].find(name_asset,0)) != -1 :

            asset_compared += 1
            #print "found"
            for checksum_single_lines in checksum_all_lines :
                checksum_inner_data = str(checksum_single_lines).split(" ")
                #print "ftp_inner_data: %s , checksum_inner_data : %s" %(ftp_inner_data[0].strip(), checksum_inner_data[2].swapcase().strip())
                if ftp_inner_data[0].strip() == checksum_inner_data[2].swapcase().strip() :
                    ok_counter += 1
                    #print "Identical"
                    pass
                else :
                    print "MD5 is different :\n Original file & md5 : %s - %s \n Ingested file : Extrenal ID : %s - Asset name : %s - md5 : %s\n" % (ftp_inner_data[0],ftp_inner_data[1], checksum_inner_data[0], checksum_inner_data[1], checksum_inner_data[2]  )
                    bad_counter += 1
    
    
    
    elif all_assets_checksum == 'y' : 
        print "All : BEFORE Comparing asset : %s" %(ftp_inner_data[1])
        print "All : BEFORE asset name : %s" %(name_asset)
        for checksum_single_lines in checksum_all_lines :
            print "checksum line--> %s\n" % (checksum_single_lines)
            checksum_inner_data = str(checksum_single_lines).split(" ")
            #asset_compared += 1
            if (checksum_inner_data[1].find(ftp_inner_data[1],0)) != -1 :
                asset_compared += 1
                print "in : ftp asset = %s , asset_checksum_file = %s" %(ftp_inner_data[1],checksum_inner_data[1])
                if ftp_inner_data[0].strip() == checksum_inner_data[2].swapcase().strip() :
                    ok_counter += 1
                    #print "Identical"
                    pass
                else :
                    print "MD5 is different :\n Original file & md5 : %s - %s \n Ingested file : Extrenal ID : %s - Asset name : %s - md5 : %s\n" % (ftp_inner_data[0],ftp_inner_data[1], checksum_inner_data[0], checksum_inner_data[1], checksum_inner_data[2]  )
                    bad_counter += 1
                
            #print "found"
        
            else :
                pass
            
    else :
        pass

print "\n\nTotal of %s files was/were compared : \n\t\t\t\t  %s of them were identical \n\t\t\t\t  %s of them were different." % (asset_compared, ok_counter, bad_counter)
                                  
   
    
    
