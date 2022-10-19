import sys
import time
import datetime

def strptime(string,format):
    if sys.version_info <  (2, 5):
        return datetime.datetime(*(time.strptime(string,format)[0:6]))
    else:
        return datetime.datetime.strptime(string,format)



