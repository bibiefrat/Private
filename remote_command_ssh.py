import urllib2, datetime, sys, subprocess
import traceback,os
from pexpect import pxssh 

try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET


db_addr = '10.65.132.12'
db_machine_password = 'F@brix'
ch_name='adi_0'
timeout = ''
data_id = []
vol="fxpod-vol"
blade="10.65.132.17"


#query="select external_id,data_id from asset where external_id like \'%%%s%%_abr%%\' and active=1 and error_code=0" %  str(ch_name)
cmd = '''/opt/solidDB/soliddb-6.5/bin/solsql -x onlyresults -e "select data_id from asset where external_id like '%''' + ch_name + '''%_abr%' and active=1 and error_code=0" 'tcp 2315' fabrix fabrix'''
print "query: " +  cmd

s = pxssh.pxssh()
s.force_password = True
s.login(db_addr, 'root', db_machine_password)
s.sendline("clear")
s.prompt()
s.sendline(cmd)
s.prompt()
output = s.before
print output
