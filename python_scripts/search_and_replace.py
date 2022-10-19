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
    replace('/tmp/config.ini',"total_ingests = .*",'total_ingests = 55')
    
if __name__ == "__main__":
    main()
