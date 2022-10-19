import urllib2, datetime, sys, subprocess
import traceback,os
from pexpect import pxssh 

try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET

manager= '10.10.61.7'
db_addr = '10.10.61.7'
# either postgres or solid
db_type='postgres'
db_machine_password = 'F@brix'
ch_name='ch_0'
timeout = ''
data_id = []
vol="edge-vol"
#vol="rack-pod-2-vol"
blade="10.10.61.13"
#either edge or jitx
vfile_jitx_or_vspp_edge="edge"
# percent of assets to delete in edge in order pull them from origin again: 0-100
percent_of_new_assets_to_play=100

#either 9999 for HA or 5432 for single
postgres_port=5432

def amount_of_assets_to_del_as_to_percent():
    if vfile_jitx_or_vspp_edge == "edge":
        if db_type=='solid':
            cmd = '''/opt/solidDB/soliddb-6.5/bin/solsql -x onlyresults -e "select count(*) from cm_file" 'tcp 2315' fabrix fabrix'''
        else:
            cmd = '''PGPASSWORD=fabrix psql -t -U fabrix -d manager -h %s -p %s -c "select count(*) from cm_file"''' % (str(db_addr),str(postgres_port))
        s = pxssh.pxssh()
        s.force_password = True
        s.login(db_addr, 'root', db_machine_password)
        s.sendline("clear")
        s.prompt()
        s.sendline(cmd)
        s.prompt()
        output = s.before
        for line in output.split("\n"):
            try:
                if isinstance(int(line), int):
                    x = line 
            except:
                pass           
        print x
        return (float(x))
    
num_total_asset = amount_of_assets_to_del_as_to_percent()

if vfile_jitx_or_vspp_edge == "jitx":
    if db_type=='solid':
#query="select external_id,data_id from asset where external_id like \'%%%s%%_abr%%\' and active=1 and error_code=0" %  str(ch_name)
        cmd = '''/opt/solidDB/soliddb-6.5/bin/solsql -x onlyresults -e "select data_id from asset where external_id like '%''' + ch_name + '''%_abr%' and active=1 and error_code=0" 'tcp 2315' fabrix fabrix'''
    else:
        cmd = '''PGPASSWORD=fabrix psql -t -U fabrix -d manager -h %s -p %s -c "select data_id from asset where external_id like '%''' + ch_name + '''%_abr%' and active=1 and error_code=0"''' % (str(db_addr),str(postgres_port))
if vfile_jitx_or_vspp_edge == "edge":
    num_asset_to_del = int((float(percent_of_new_assets_to_play) / 100) * num_total_asset)
    if db_type=='solid':
        cmd = '''/opt/solidDB/soliddb-6.5/bin/solsql -x onlyresults -e "select file_name from cm_file limit %s" 'tcp 2315' fabrix fabrix''' % str(num_asset_to_del)
    else: 
        cmd = '''PGPASSWORD=fabrix psql -t -U fabrix -d manager -h %s -p %s -c "select file_name from cm_file limit %s" > /tmp/1.txt ; cat /tmp/1.txt''' % (str(db_addr),str(postgres_port),str(num_asset_to_del))

print "query: " +  cmd

#x = '''expect -c "set timeout -1;
#spawn ssh %s -l root \\"cd /opt/solidDB/soliddb-6.5/bin ;for i in $\(seq 1 1\); do \(./solsql -e ""%s"" \'tcp 2315\' fabrix fabrix  ;sleep 1 \); done; exit;\\";
#match_max 100000;
#expect *password:*;
#send -- %s\\r;
#interact;" | grep -i '  [0-9]* ' | grep -v 'ID' | grep -v '\\-\\-' | grep -v rows > tmp.db  '''  % (str(db_addr),str(query),str(db_machine_password))
#try:
#   print x
#   os.system(x)
#except:
#    traceback.print_exc(file=sys.stdout)

#child = pexpect.spawn ('ssh root@10.65.132.163')
#child.expect ('root@10.65.132.163\'s password:')
s = pxssh.pxssh()
s.force_password = True
s.login(db_addr, 'root', db_machine_password)
s.sendline("clear")
s.prompt()
s.sendline(cmd)
s.prompt()
output = s.before
print output
if vfile_jitx_or_vspp_edge == "edge":
    for line in output.split("\n"):
        if db_type=='solid':
            if "solsql" not in line.strip() and line.strip() != '':
                vfile=line.strip().split("/")
                print vfile[1]
                data_id.append(vfile[1].strip())
        else:
            if str(vol) in line.strip() and line.strip() != '':
                vfile=line.strip().split("/")
                print vfile[1]
                data_id.append(vfile[1].strip())
if vfile_jitx_or_vspp_edge == "jitx":
    for line in output.split("\n"):
        if db_type=='solid':
            if "solsql" not in line.strip() and line.strip() != '':
                data_id.append(line.strip())
        else:
            if str(vol) in line.strip() and line.strip() != '':
                data_id.append(line.strip())
print data_id 
#print "last elem: " + data_id[len(data_id)-1] + "."
#print "len: " + str(len(data_id))

def find_vfile_and_delete2():
    global vol,blade,data_id
    for file in data_id:
        url = '''http://%s:5925/FX_PVFS_File_Test/POSIX_Read_Meta_Inode?file_path=%s&volume_name=%s&cluster_name=%s&cluster_port=1928&is_new_format=1&object_name=''' % (str(blade) ,str(file),str(vol),str(manager)) 
        print url
        try:
            res = urllib2.urlopen(url).read()
        except urllib2.HTTPError, e:
            print 'Problem sending request:'
            print url
            print e
            sys.exit(1)
    #    print res    
        asset_xml = ET.fromstring(res)
        #print   asset_xml     
    #    tree = ET.parse(str(asset_xml))
    #    root = tree.getroot()
        tree = ET.ElementTree(ET.fromstring(res))
        root = tree.getroot()
        for elem in root.iter("streams"):            
            #ET.dump(elem)
            for x in elem.iter():
                print x.tag
                #size = x.find('size').text
                #print size
            
      
def find_vfile_and_delete():
    global vol,blade,data_id,manager
    for file in data_id:
        file = urllib2.quote(file, safe='')
        url = '''http://%s:5925/FX_PVFS_File_Test/POSIX_Read_Meta_Inode?file_path=%s&volume_name=%s&cluster_name=%s&cluster_port=1928&is_new_format=1&object_name=''' % (str(blade) ,str(file),str(vol),str(manager)) 
        print url
        try:
            res = urllib2.urlopen(url).read()
        except urllib2.HTTPError, e:
            print 'Problem sending request:'
            print url
            print e
            sys.exit(1)
    #    print res    
        asset_xml = ET.fromstring(res)
        #print   asset_xml     
    #    tree = ET.parse(str(asset_xml))
    #    root = tree.getroot()
        if vfile_jitx_or_vspp_edge == "jitx":
            for elem in asset_xml.findall(".//meta_inode/streams/elem/stream_name"):
               if elem.text.find("mpg_") > 0:
                    print "Send Delete: " + (elem.text)
                    url_to_del_basic="http://%s:5929/FX_CM_Service/FX_Delete_Inner_Files?size=0&single_stream=" % str(manager)
                    url_to_del_quote = "%s/%s" % (str(vol),str(elem.text))
                    res = urllib2.quote(url_to_del_quote, safe='')
                    #print res
                    url_to_del = url_to_del_basic + res
                    #print url_to_del
                    res = urllib2.urlopen(url_to_del).read()
                    print "Reply: " + res
    
            #tree = ET.parse(res)
            #root = tree.getroot()
            #print root.tag    
    
        if vfile_jitx_or_vspp_edge == "edge":
           for elem in asset_xml.findall(".//meta_inode/meta_inode_file_info/file_name"):
               if elem.text.find("repackage_origin") > 0:
                    print "Send Delete: " + (elem.text)
                    file_id=urllib2.quote(elem.text, safe='')
                    url_to_del_basic = "http://%s:5929/FX_CM_Service/FX_Delete_File?file_path=%s&force_delete=1&file_id=0&fs_version=1&delete_single_file=0" % (str(manager), str(file_id))             
#                    print url_to_del_basic
                    res = urllib2.urlopen(url_to_del_basic).read()
                    print "Reply: " + res
#                    print 1
#            for elem in asset_xml.findall(".//meta_inode/streams/elem/stream_name"):
#               if elem.text.find("repackage_origin") > 0:
#                    print "Send Delete: " + (elem.text)
#                    url_to_del_basic="http://%s:5929/FX_CM_Service/FX_Delete_Inner_Files?size=0&single_stream=" % str(manager)
#                    url_to_del_quote = "%s/%s" % (str(vol),str(elem.text))
#                    res = urllib2.quote(url_to_del_quote, safe='')
                    #print res
#                    url_to_del = url_to_del_basic + res
                    #print url_to_del
#                    res = urllib2.urlopen(url_to_del).read()
#                    print "Reply: " + res
    
            #tree = ET.parse(res)
            #root = tree.getroot()
            #print root.tag        
    

find_vfile_and_delete()

