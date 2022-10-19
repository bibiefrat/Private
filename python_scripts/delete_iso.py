#! /usr/lib/python2.7

import time
import re
import sys
import pexpect
import os
import fileinput
import ConfigParser
import socket
import sys,getopt
import shlex
import datetime
import smtplib
import requests
import subprocess
from datetime import datetime
from subprocess import Popen, PIPE

#import deploy_conf as conf

def getMetaData():
            """
            input : None
            output: meta data in JSON format
                    should be matching the version given to class instance
            """
            req_url = '/iso/list'
            base_url= 'http://192.168.5.58:8080/api'
            full_url = "%s%s" % (base_url, req_url)
            response = requests.get(full_url)
            print ("Response: %s") % str(response.status_code)
            if response.status_code != 200:
                msg = "\nISO meta data request failed. exiting.\n"
                sys.exit(msg)
            json_data = response.json()
#           print json_data
            return json_data            
            

def filterDataByDate(meta_data,older_than_days):
    global Iso_To_Del
    for entry in meta_data:
        ID = entry['Id']
        ModifyDate = entry['ModifyDate']
        Comment = entry['Comment']
#        print Comment
#        print "ISO info: %s , %s" % (str(ID),str(ModifyDate))
        format = '%d/%b/%Y %I:%M:%S%p'
        myModifyDate  = datetime.strptime(ModifyDate, format )
#        print myModifyDate.strftime(format)
        time_between_insertion = datetime.now() - myModifyDate
        # Delete ISO created by automation alder than month
        if Comment.rstrip() == '':
          Iso_To_Del[ID] =  str(ModifyDate)
          pass 
        
        match = re.search('^_20(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)Z', Comment)
        if match:
            Comment = Comment[1:]
            format = '%Y-%m-%dT%H:%M:%SZ'
            automation_date= datetime.strptime(Comment, format)
            #print automation_date
            time_between_automation_insertion = datetime.now() - automation_date            
        else:
            time_between_automation_insertion = datetime.now() -  datetime.now()
                          
        if  time_between_insertion.days > older_than_days or time_between_automation_insertion.days > 30:
#            print "old iso " + str(myModifyDate)
            if time_between_automation_insertion.days > 30:
                print  "delete automatio ISO older than month: " + str(automation_date) + "with ID: " + str(ID)
            Iso_To_Del[ID] =  str(ModifyDate)            
    return Iso_To_Del


def getISOstatusById(id):

       """
       input : iso id 
       output : a json containing the iso svn versions 
       """ 
       req_url = '/iso/status/%s' %id
       base_url= 'http://192.168.5.58:8080/api'
       
       full_url = "%s%s" % (base_url, req_url)
       print (full_url)
       response = requests.get(full_url)

       print ("Response: %s") % str(response.status_code)
       if response.status_code != 200:
            msg = "\nISO meta data request failed. exiting.\n"
            sys.exit(msg)
       json_data = response.json()
       print(type(json_data))

       #print (json_data)
       return json_data

def numOfIso(meta_data):
    counter = 0
    for entry in meta_data:
        counter += 1
    return counter


def delById(Iso_To_Del):
    for iso in Iso_To_Del:
        print "status before: " + str(getISOstatusById(iso))
        req_url = '/iso/delete/%s' % iso
        base_url= 'http://192.168.5.58:8080/api'
        full_url = "%s%s" % (base_url, req_url)
        print (full_url)
        response = requests.get(full_url)
        print ("Response: %s") % str(response.status_code)
        if response.status_code != 200:
            msg = "\nISO meta data request failed. exiting.\n"
            sys.exit(msg)
        print "status after: " + str(getISOstatusById(iso))

def main(argv):
    print "Start del iso script"
    global Iso_To_Del
    older_than_days = 730
    Iso_To_Del = {}
    filterDataByDate(getMetaData(),older_than_days)    
    delById(Iso_To_Del)
    
    numberOfIsos = numOfIso(getMetaData())
    print "current Num Of Iso: " +  str(numberOfIsos)
    if numberOfIsos >= 2000:
        Iso_To_Del = {}#    subprocess.call(['ls', '-1'], shell=True)
        filterDataByDate(getMetaData(),older_than_days)
        delById(Iso_To_Del)    
        Iso_To_Del = {}
        numberOfIsos = numOfIso(getMetaData())
        older_than_days =  older_than_days - 20
        print "current Num Of Iso: " +  str(numberOfIsos)

if __name__ == "__main__":
    main(sys.argv[1:])
    
    
    