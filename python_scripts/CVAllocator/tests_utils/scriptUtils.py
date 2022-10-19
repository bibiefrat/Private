'''
Created on Aug 21, 2014

@author: yuval

Utilities to run testing scripts

'''
import subprocess
from datetime import timedelta
from time import sleep 
from xml.etree import ElementTree
import uuid

def createUniqueID():
    '''
    Returns a unique UUID. 
    '''
    _NUM_BITS_IN_ID = 48    # length (in bits) of the random ID generated
    _NUM_BITS_ERASE = 128 - _NUM_BITS_IN_ID

    return str(uuid.uuid1().int >> _NUM_BITS_ERASE)

def createUniqueName(name, separatingSymbol = '_'):
    '''
    Returns a name that contains a unique UUID. 
    @param name: This string will be concatenated before the UUID
    @param separatingSymbol: A separating symbol between the name and the UUID. To give up the symbol, simply define it as ''. Default: '_'
    '''
    return name + separatingSymbol + createUniqueID()

def getGlobalConfs(confNames,fromINIFile = False, pathToFile = '/opt/Fabrix.TV/Manager/bin/manager.use'):
    '''
    gets a list of all desired global confs and returns a dictionary with their values.
    if a global conf is not in the file, it will be absent from the return dictionary
    @param confNames: a list containing the names of the desired global confs
    @param fromINIFile: True to bring the confs from INI file instead of USE file. If set to true, change also param pathToFile. default: False
    @param pathToFile: An option to get confs from another file. Default is /opt/Fabrix.TV/Manager/bin/manager.use
    @return: a dictionary: {confName1: conf1Value, conf2Name: conf2Value ...}
    '''
    # variables to hold the differences in strings between USE file and INI file
    if fromINIFile:
        sharpSign = ''
    else:
        sharpSign = '# '
    
    # get all global confs lines
    cmd = ''
    for conf in confNames:
        cmd = cmd + 'cat ' + pathToFile + ' | grep -iE "^' + sharpSign + conf + ' = .*$";'
        
    #print 'Running this cmd: ' + cmd
    output = runCmd(cmd)
    
    # return the real values in a dictionary
    values = {}
    lines = str(output).splitlines()
    for line in lines:
        if line != '':
            name = line.split('=')[0].lstrip('#').strip()
            value = line.split('=')[1].strip()
            values[name] = value

    return values

def changeGlobalConfs(confs,pathToINI,killPath=''):
    '''
    gets a dictionary with global confs names and their new values. Changes the INI file and kills -1 the process.
    @param confs: A dictionary that contains the name of the global confs to be changed and the new value to put in them.
    @param pathToINI: The path to the INI file that contains the global confs
    @param killPath: Sends kill -1 to the process that was ran from this path. default: empty string (don't kill)
    @return: A function that once called, restores all global confs that were changed to their old value, and deletes new added confs
    '''
    
    ''' update existing confs in INI file and add new confs to INI file (confs that weren't in the file before) '''
    
    # get the confs from the ini file
    oldINIConfs = getGlobalConfs(confs.keys(),True,pathToINI)
    
    print 'oldINIConfs: ' + str (oldINIConfs) 
    
    # prepare command strings. examples:
    # update: sed -i 's/ENABLE_ROLLING_BUFFER_INGEST_RESILIENCY = false/ENABLE_ROLLING_BUFFER_INGEST_RESILIENCY = true/' /opt/Fabrix.TV/Manager/bin/manager.ini;
    # add: echo "ENABLE_ROLLING_BUFFER_INGEST_RESILIENCY = true" >> /opt/Fabrix.TV/Manager/bin/manager.ini
    
    cmdUpdate = ''
    cmdAdd = ''
    for conf,newValue in confs.iteritems():
        if conf in oldINIConfs:
            cmdUpdate = cmdUpdate + "sed -i 's/" + str(conf).upper() + " = " + str(oldINIConfs[conf]) + \
            "/" + str(conf).upper() + " = " + str(newValue).lower() + "/' " + pathToINI  + "; "
        else:
            cmdAdd = cmdAdd + 'echo "' + str(conf).upper() + ' = ' + str(newValue).lower() + '" >> ' + pathToINI + '; '
            
    print 'Running this cmdUpdate + cmdAdd: ' + cmdUpdate + cmdAdd
    runCmd(cmdUpdate + cmdAdd)

    #print 'Killing the process in: ' + killPath
    killProcess(killPath)
    
    
    #return a restore() function that restores the old values, deletes the new confs, and kills -1 the process 
    def restoreGlobalConfs():
        # TODO: simply use sed -i to save a backup file when changing INI, and change this restore function to simply copy the file back
        cmdRestoreOld = ''
        confsToDel = {}
        for conf,newValue in confs.iteritems():
            if conf in oldINIConfs:
                cmdRestoreOld = cmdRestoreOld + "sed -i 's/" + str(conf).upper() + " = " + str(newValue).lower() + \
                "/" + str(conf).upper() + " = " + str(oldINIConfs[conf]) + "/' " + pathToINI + "; "
            else:
                confsToDel[conf]=newValue
        print 'Running this cmdRestoreOld: ' + cmdRestoreOld
        runCmd(cmdRestoreOld)
        delGlobalConfs(confsToDel,pathToINI)
        killProcess(killPath)
    
    return restoreGlobalConfs
   
    
def delGlobalConfs(confs,pathToINI):
    '''
    gets a dictionary containing the conf and its current value, and deletes the conf
    (this function should be changed to be able to delete the conf even without its value.
    it is required to find how the sed command can do it)
    '''
    # EXample: sed -i '/ENABLE_ROLLING_BUFFER_INGEST_RESILIENCY = true/d' /opt/Fabrix.TV/Manager/bin/manager.ini;
    cmd = ''
    for conf,value in confs.iteritems():
        cmd = cmd + "sed -i 's/" + str(conf).upper() + " = " + str(value).lower() + "/d' " + pathToINI + "; "
    
    print 'Running this delGlobalConfs cmd: ' + cmd
    runCmd(cmd)
    

    
def killProcess(killPath):
    WAIT_TIME_AFTER_KILL = 1 #seconds
    if killPath != '' :
        cmd = "kill -1 `ps -ef | grep -i " + killPath + " | grep -v grep | awk '{print $2}'`"
        print 'killing process with cmd: ' + cmd
        runCmd(cmd)
        sleep(WAIT_TIME_AFTER_KILL) # wait a little time for the process to restart
    
def runCmd(cmd):
    '''
    runs CMD on current machine
    '''
    if cmd == '':
        return ''
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()    
    if err is not None:
        print 'runCmd ERROR:'
        print err
    return output    

def strToTimeDelta(strTime):
    '''
    string must be in this format: hh:mm:ss.milisecs
    '''
    times = strTime.split(':')
    hours = int(times[0])
    mins = int(times[1])
    secs = int(times[2].split('.')[0])
    milisecs = int(times[2].split('.')[1])
    return timedelta(hours=hours,minutes=mins,seconds=secs,milliseconds=milisecs)






