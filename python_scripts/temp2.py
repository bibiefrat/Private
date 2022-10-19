#! /usr/bin/python

import urllib2, datetime, sys, subprocess
try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET


def create_ids_list(mgr_ip):
    """
    Get region, edge and streamer ids
    """
    topo_str = send_url("http://%s:5929/topology_get_regions?X=0" % mgr_ip)
    ids_list = []
    topo_xml = ET.fromstring(topo_str)
    region = topo_xml.find("regions/elem")
    region_id = region.find("id").text
    for edge in region.findall("edges/elem"):
        edge_id = edge.find("id").text
        for streamer in edge.findall("streamers/elem"):
            streamer_id = streamer.find("id").text
            ids_list.append((mgr_ip, region_id, edge_id, streamer_id))
    return ids_list
    

def find_negative_bw(monitor_xml):
    """
    For each disk in the streamer, find negative bw and return when it happend
    """
    negative_bw_list = []
    disks = monitor_xml.findall("disks/elem")
    for disk in disks:
        disk_index = disk.attrib['id']
        for time_frame in disk.findall("ingest/allocation_schedule/elem"):
            bw = int(time_frame.find("bandwidth").text)
            if bw < 1:
                start_time = datetime.datetime.utcfromtimestamp(float(time_frame.find("start").text))
                end_time = datetime.datetime.utcfromtimestamp(float(time_frame.find("end").text))
                negative_bw_list.append((disk_index, bw, start_time, end_time))
    return negative_bw_list

def find_negative_bw_no_FPR(monitor_xml):
    """
    For each disk in the streamer, find negative bw and return when it happend
    """
    negative_bw_list = []
    #disks = monitor_xml.findall("disks/elem")
    #for disk in disks:
        #disk_index = disk.attrib['id']
    for time_frame in monitor_xml.findall("ingest/allocation_schedule/elem"):
        bw = int(time_frame.find("bandwidth").text)
        if bw < 1:
            start_time = datetime.datetime.utcfromtimestamp(float(time_frame.find("start").text))
            end_time = datetime.datetime.utcfromtimestamp(float(time_frame.find("end").text))
            negative_bw_list.append((bw, start_time, end_time))
    return negative_bw_list


def send_url(url):
    """
    Send requests and handle exceptions
    """
    req = urllib2.Request(url)
    try:
        res = urllib2.urlopen(req).read()
    except urllib2.HTTPError, e:
        print 'Problem sending request:'
        print url
        print e
        sys.exit(1)
    except urllib2.URLError, e:
        print 'Problem sending request:'
        print url
        print e.reason
        sys.exit(1)
    return res


def find_last_playable(mgr_ip,mgr_port,channel):    
    res = send_url("http://%s:%s/mixed_status_rolling_buffer/%s/2013-11-01T00:00:00Z/2015-06-23T23:59:00Z" % (mgr_ip, mgr_port, channel))
    inner_buf_xml = ET.fromstring(res)
    inner_buf = inner_buf_xml.findall(".//channel[@bitrate_type='ABR']/inner_buffer[@playable]")    
    for inner in inner_buf:
        start_time = inner.get('start_time')
        end_time = inner.get('end_time')
        print start_time
        print end_time
        
    print res


def usage():
    print "%s <mgr_ip> <port> <channel>" % sys.argv[0]
    sys.exit(1)


def main():
    # Check args
    if len(sys.argv) == 4:
        mgr_ip = sys.argv[1]
        mgr_port = sys.argv[2]
        channel = sys.argv[3]    
    else:
        usage()    
    
    
    find_last_playable(mgr_ip,mgr_port,channel)
    

    # Get times
#    tz_offset = int(subprocess.Popen("""echo `date +%:z | awk -F ":" ' { print $1 } '`""", shell=True, stdout=subprocess.PIPE).stdout.readline().replace("\n", ""))
#    adjust_gmt = datetime.timedelta (hours=-1 * tz_offset)
#    day_begin = datetime.datetime(int(req_date[:4]), int(req_date[5:7]), int(req_date[8:])) + adjust_gmt

    # Find region, edge and streamer ids
#    ids_list =  create_ids_list(mgr_ip)
 #   for ids in ids_list:
       #print "http://%s:5929/command/monitor_service?token=&agent=&id=TOPOLOGY&opaque=%s+%s+%s" % ids,
       # For each streamer, check negative bw
 #      monitor_str = send_url("http://%s:5929/command/monitor_service?token=&agent=&id=TOPOLOGY&opaque=%s+%s+%s" % ids)
#       monitor_xml = ET.fromstring(monitor_str)
#       if is_fpd == 'fpd':  
#           negative_bw_list = find_negative_bw(monitor_xml)
#       else:
#           negative_bw_list = find_negative_bw_no_FPR(monitor_xml)
       #print len(negative_bw_list)
#       for neg in negative_bw_list:
           # For each time frame with negative bw, check if the time frame is in the requested date
#           if (neg[1] - day_begin).days >= 0:
#               print "Negative bw found! region: %s edge: %s streamer: %s start time: %s end time: %s bw: %s" % (ids[1], ids[2], ids[3], neg[1], neg[2], neg[0])




if __name__ == "__main__":
    main()
