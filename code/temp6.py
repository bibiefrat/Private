import time
import datetime
import struct

t=time.localtime(time.time())
print t.tm_year
print t
t1=datetime.datetime.now()
print t1.time()
print  datetime.datetime.now() - datetime.datetime(2012, 12, 31, 23, 59, 59)
print struct.pack('I', 70000)