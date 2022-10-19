import math
import sys
import os
import string
import urllib2
import urllib
import libxml2
from configobj import ConfigObj
import xml.sax.saxutils
import socket
import random
from bisect import bisect
import xml.etree.ElementTree as ET

class globalParams:
    def __init__(self):
        self.manager = ""
     

def pars_INI_file(configFile):
    global params
    global Region_ID
    global Edge_ID
    
    params.manager = configFile['Configuration']['manager']
    params.multicast_addr = configFile['Configuration']['multicast_addr']
    params.one_fake_machine = int(configFile['Configuration']['one_fake_machine'])
    params.start_port = int(configFile['Configuration']['starting_port'])
    params.bandwidth = configFile['Configuration']['bandwidth']
    params.log_file =  configFile['Configuration']['log_file_location']
    params.num_channel_map = int(configFile['Configuration']['num_channel_map'])
    params.channel_prefix = configFile['Configuration']['channel_prefix']
    params.channel_source = configFile['Configuration']['channel_source']
    params.ad_zone_prefix = configFile['Configuration']['ad_zone_prefix']
    params.ad_zone_identical = int(configFile['Configuration']['ad_zone_identical'])
    params.is_abr_channel = int(configFile['Configuration']['is_abr_channel'])
    params.layers_bw = ','.join(configFile['Configuration']['layers_bw'])
    params.source_addr = str(configFile['Configuration']['source_addr'])
    params.monitor = int(configFile['Configuration']['monitor'])
    params.only_one_multicast = int(configFile['Configuration']['only_one_multicast'])
    params.cbr_live = int(configFile['Configuration']['cbr_live'])
    params.delete_channels = str(configFile['Configuration']['delete_channels'])
    params.size_delete_channels = int(configFile['Configuration']['size_delete_channels'])
    params.delete_abr_cbr = int(configFile['Configuration']['delete_abr_cbr'])
    params.delete_cbr_live = int(configFile['Configuration']['delete_cbr_live'])
    params.update_channels = int(configFile['Configuration']['update_channels'])
    params.cbr_layer_type_for_cvc = str(configFile['Configuration']['cbr_layer_type_for_cvc'])
    params.multicast_for_cbr = str(configFile['Configuration']['multicast_for_cbr'])
    params.multicast_start_port_for_cbr = str(configFile['Configuration']['multicast_start_port_for_cbr'])
    params.pods_dist_to_chnl = str(configFile['Configuration']['pods_dist_to_chnl']).strip()
    params.pods_ids = str(configFile['Configuration']['pods_ids']).strip()
    params.use_edge_ids = int(configFile['Configuration']['use_edge_ids'])
    params.cbr_layers_bw = ','.join(configFile['Configuration']['cbr_layers_bw'])
    params.sc_enable = int(configFile['Configuration']['sc_enable'])
    params.abr_live = int(configFile['Configuration']['abr_live'])
    params.cbr_igmp_source_addr = str(configFile['Configuration']['cbr_igmp_source_addr']).strip()
    params.pause = int(configFile['Configuration']['pause'])
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////// 
def wchoice(objects, frequences, filter=True, normalize=True):
    """wchoice(objects, frequences, filter=True, normalize=True): return
    a function that return the given objects with the specified frequency
    distribution. If no objects with frequency>0 are given, return a
    constant function that return None.

    Input:
      objects: sequence of elements to choose.
      frequences: sequence of their frequences.
      filter=False disables the filtering, speeding up the object creation,
        but less bad cases are controlled. Frequences must be float > 0.
      normalize=False disables the probablitity normalization. The choice
        becomes faster, but sum(frequences) must be 1
    """
    if filter:
        # Test and clean the frequencies.
        if isinstance(frequences, (set, dict)):
            raise "in wchoice: frequences: only ordered sequences."
        if isinstance(objects, (set, dict)):
            raise "in wchoice: objects: only ordered sequences."
        if len(frequences) != len(objects):
            raise "in wchoice: objects and frequences must have the same lenght."
        frequences = map(float, frequences)
        filteredFreq = []
        filteredObj = []
        for freq, obj in izip(frequences, objects):
            if freq < 0:
                raise "in wchoice: only positive frequences."
            elif freq >1e-8:
                filteredFreq.append(freq)
                filteredObj.append(obj)

        if len(filteredFreq) == 0:
            return lambda: None
        if len(filteredFreq) == 1:
            return lambda: filteredObj[0]
        frequences = filteredFreq
        objects = filteredObj
    else:
        if len(objects) == 1:
            return lambda: objects[0]
        # Here objects is unaltered, so it must have a fast __getitem__

    addedFreq = []
    lastSum = 0
    for freq in frequences:
        lastSum += freq
        addedFreq.append(lastSum)

    # If the choice method is called many times, then the frequences
    # can be normalized to sum 1, so instead of random()*self.sumFreq
    # a random() suffices.
    if normalize:
        return lambda rnd=random.random, bis=bisect: objects[bis(addedFreq, rnd()*lastSum)]
    else:
        return lambda rnd=random.random, bis=bisect: objects[bis(addedFreq, rnd())]


 
 
    
def get_all_channels():
    global params
    global channels_to_del
    global channels_to_del_is_abr
    global channels_to_del_is_cbr
    url = "http://%s/multicast_channel/get_all?offset=0&limit=10000" % (params.manager)
    all_channels = urllib2.urlopen(url)
    xml = all_channels.read()
    channels_list = libxml2.parseDoc(xml)    
    xpath="//X/value/total"       
    list = channels_list.xpathEval(xpath)
    for node in list:
        print "Total Channel in System = %s" %  str(node.content)
    #xpath="//X/value/channels/elem/name"
    xpath_all='''//X/value/channels/elem/name'''
    list = channels_list.xpathEval(xpath_all)
    for node in list:   
        channels_to_del.append(node.content)
    
    xpath_abr='''//X/value/channels/elem'''        
    list = channels_list.xpathEval(xpath_abr)
    for node in list:
        if(('''<abr>
    </abr>''' in str(node)) or ('''<abr>''' not in  str(node))):
            print "cbr -> " + node.get_children().next.content
            if '''<cbr_live>1</cbr_live>''' in str(node) and params.delete_cbr_live == 1:
                print "CBR live" 
                channels_to_del_is_cbr.append(node.get_children().next.content)
            if '''<cbr_live>1</cbr_live>''' in str(node) and params.delete_cbr_live != 1:
                pass
            if '''<cbr_live>1</cbr_live>''' not in str(node) and params.delete_cbr_live == 0:
                print "CBR not live" 
                channels_to_del_is_cbr.append(node.get_children().next.content)
            
        else:
            print "abr -> " + node.get_children().next.content
            channels_to_del_is_abr.append(node.get_children().next.content)
            
    delete_channels()
    
def delete_channels():
    global params
    global channels_to_del
    global channels_to_del_is_abr
    global channels_to_del_is_cbr
    j = params.size_delete_channels
    
    if params.size_delete_channels == 0:
        if params.delete_abr_cbr == 0:
            for i in channels_to_del:
                try:
                    url="http://%s/multicast_channel/delete_by_name?X=%s" %( params.manager, urllib.quote_plus(i))
                    urllib2.urlopen(url)
                    print "delete: " + str(url)
                except:
                    pass
        if params.delete_abr_cbr == 1:
            for i in channels_to_del_is_cbr:
                try:
                    url="http://%s/multicast_channel/delete_by_name?X=%s" %( params.manager, urllib.quote_plus(i))
                    urllib2.urlopen(url)
                    print "delete: " + str(url)
                except:
                    pass
        if params.delete_abr_cbr == 2:
            for i in channels_to_del_is_abr:
                try:
                    url="http://%s/multicast_channel/delete_by_name?X=%s" %( params.manager, urllib.quote_plus(i))
                    urllib2.urlopen(url)
                    print "delete: " + str(url)
                except:
                    pass
    else:        
        if params.delete_abr_cbr == 0:
            for i in channels_to_del:
                try:
                    if j > 0:
                        url="http://%s/multicast_channel/delete_by_name?X=%s" %( params.manager, urllib.quote_plus(i))
                        urllib2.urlopen(url)
                        print "delete: " +  str(url)
                        j = j - 1
                    else:
                        break
                except:
                    pass
        if params.delete_abr_cbr == 1 :
            for i in channels_to_del_is_cbr:
                try:
                    if j > 0:
                        url="http://%s/multicast_channel/delete_by_name?X=%s" %( params.manager, urllib.quote_plus(i))
                        urllib2.urlopen(url)
                        print "delete: " + str(url)
                        j = j - 1
                    else:
                        break
                except:
                    pass
        if params.delete_abr_cbr == 2 :
            for i in channels_to_del_is_abr:
                try:
                    if j > 0:
                        url="http://%s/multicast_channel/delete_by_name?X=%s" %( params.manager, urllib.quote_plus(i))
                        urllib2.urlopen(url)
                        print "delete: " + str(url)
                        j = j - 1
                    else:
                        break
                except:
                    pass
    
    
    
    
    
def str_stb_ip_parse(ip):
    
        ip[0] = str(ip[0]) 
        ip[1] = str(ip[1])
        ip[2] = str(ip[2])
        ip[3] = str(ip[3])   
       
        new_ip = '.'.join(ip)
        
        return new_ip

def my_is_int(str):
     try:
         int(str)
         return True
     except:
         return False


def my_is_float(str):
     try:
         float(str)
         return True
     except:
         return False
    
def stb_ip_parse(ip):
        ipNums = ip.split('.')
        if len(ipNums) != 4:
            ipNums = []
            for i in range(4): 
                ipNums.append('f')
        if (ipNums[0] == ''):
            ipNums[0] = 'f'
        elif (my_is_int(ipNums[0]) != True)  :
            ipNums[0] = 'f'
        else:
            ipNums[0] = int(ipNums[0])
        if (ipNums[1] == ''):
            ipNums[1] = 'f'   
        elif (my_is_int(ipNums[1]) != True):
            ipNums[1] = 'f'   
        else:
            ipNums[1] = int(ipNums[1])
        if (ipNums[2] == ''):
            ipNums[2] = 'f'    
        elif (my_is_int(ipNums[2]) != True):
            ipNums[2] = 'f'
        else:
            ipNums[2] = int(ipNums[2])
        if (ipNums[3] == ''):
            ipNums[3] = 'f'
        elif (my_is_int(ipNums[3]) != True):
            ipNums[3] = 'f'
        else:
            ipNums[3] = int(ipNums[3])
        
        return ipNums


def ConChannelMap(version_num):
    global params
    channels = []
    orig_start_port = params.start_port
    orig_multicast_address = params.multicast_addr
    #print "*******" , BW
           
    if params.channel_source == 'f':    
        BW = float(params.bandwidth) * 1024. * 1024.
        for i in range (params.num_channel_map):
            #if params.multiple_source == 'y' :
                           
            channel_name = "%s%s" % (params.channel_prefix,str(i))
            channel_ip = "%s:%s" % (str(params.multicast_addr),str(params.start_port))
            channels.append(channel_name)
            
            url = ""
            url += "http://"
            url += str(params.manager)
            url += "/multicast_channel/update?update=0&id=0&name="
            url += urllib.quote_plus(str(channel_name))
            url += "&addr="
            url += str(params.multicast_addr)
            url += urllib.quote_plus(":")
            url += str(params.start_port)
            url += "&bandwidth="
            url += str(BW)             
            if ((version_num[0] == 2) and (version_num[1] == 6) and (version_num[3] >= 4)) or ((version_num[0] == 2) and (version_num[1] > 6)):
                if (params.ad_zone_identical != -1) :
                    url += "&ad_zone="
                    url += str(params.ad_zone_prefix)
                    if params.ad_zone_identical==0:
                        url += str(i+1)
                    elif  params.ad_zone_identical==1:
                        url += str(1)
                    elif  params.ad_zone_identical==2:
                        pass
                
            print "*********" , url
            url_result = urllib2.urlopen(url)
            print "Channel number %d : name -> %s, MultiCast address -> %s, port -> %s, BW -> %s Mbps\n" % ((i +1), str(channel_name) , str(params.multicast_addr), str(params.start_port), str(BW))                
            if params.one_fake_machine == 1: # sending to incremental fake port
                params.start_port += 1        
            else : # Sending to incremental IP
                fake_IP_nums = stb_ip_parse(params.multicast_addr)
                #print fake_IP_nums
                if fake_IP_nums[3] > 253:
                    fake_IP_nums[3] = 0
                    fake_IP_nums[2] += 1 
                                    
                #re-assemble the fake ip string           
                fake_IP_nums[3] = int(fake_IP_nums[3])
                fake_IP_nums[3] += 1
                params.multicast_addr = str_stb_ip_parse(fake_IP_nums)
            channel_name = "%s%s" % (params.channel_prefix,str(i))
        params.start_port =  orig_start_port
        params.multicast_addr = orig_multicast_address
           
    elif params.channel_source == 'm':
        params.num_channel_map = raw_input("\nPlease enter number of channels to add \n")
        while (my_is_int(params.num_channel_map) != True):
            params.num_channel_map = raw_input("Wrong Input!!! input should be number /n Re-enter number of channels: \n")
            
            
        for i in range (int(params.num_channel_map)):
           print "Channel number : ", i+1
           channel_name = raw_input("\nPlease enter channel Name \n")
           while (channel_name == ''):
               channel_name = raw_input("\nPlease enter channel Name \n")
                      
           params.multicast_addr = raw_input("\nPlease enter channel MultiCast IP \n")
           while (CheckMultiCastIp(params.multicast_addr) != 1):
               params.multicast_addr = raw_input("\n >>>>>> Not MultiCast IP <<<<<< \n Please enter channel MultiCast ip \n")
           
           params.start_port = raw_input("\nPlease enter channel port \n")        
           while (True):
               if(my_is_int(params.start_port) != True):
                   params.start_port = raw_input("\n>>>>>> Not valid port<<<<<< \n Please enter channel port \n")
                   continue
               elif(int(params.start_port) < 0 or int(params.start_port) > 65535):
                   params.start_port = raw_input("\n>>>>>> Not a valid port Range<<<<<< \n Please enter channel port \n")
                   continue
               else:
                   break 
           
           BW = raw_input("\nPlease enter channel BW in Mbs (float representation 1.0 <---> 35.0) \n")                
           while (my_is_float(BW) != True):
               BW = raw_input("\n>>>>>> Not valid BW <<<<<< \n Please enter channel BW again in Mbs (float representation) \n")
           BW = float(BW) * 1024. * 1024.
           
           channels.append(channel_name)
            
           url = ""
           url += "http://"
           url += str(params.manager)
           url += "/multicast_channel/update?update=0&name="
           url += str(channel_name)
           url += "&addr="
           url += str(params.multicast_addr)
           url += urllib.quote_plus(":")
           url += str(params.start_port)
           url += "&bandwidth="
           url += str(BW) 
            
           #print "*********" , url
           url_result = urllib2.urlopen(url)
           print "Channel number %d : name -> %s, MultiCast address -> %s, port -> %s, BW -> %s Mbps\n" % ((i +1), str(channel_name) , str(params.multicast_addr), str(params.start_port), str(BW))                  
           
           
           
           
                                         
    return channels















def ConAbrChannelMap(version_num):
    global params
    channels = []
    
    #print "*******" , BW
           
        
    BW = int( 1024 * 1024)
    layers_bw_list = params.layers_bw.split(';')
    orig_port = params.start_port   
    for i in range (params.num_channel_map):
        #if params.multiple_source == 'y' :
        
                      
        channel_name = "%s%s" % (params.channel_prefix,str(i))
        channel_ip = "%s:%s" % (str(params.multicast_addr),str(params.start_port))
        channels.append(channel_name)
        
        url = ""
        url += "http://"
        url += str(params.manager)
        url += "/multicast_channel/update?update=0&name="
        url += urllib.quote_plus(str(channel_name))
        url += "&addr="
        url += str(params.multicast_addr)
        url += urllib.quote_plus(":")
        url += str(params.start_port)
        url += "&id=0"         
        if ((version_num[0] == 2) and (version_num[1] == 6) and (version_num[3] >= 4)) or ((version_num[0] == 2) and (version_num[1] > 6)):
            if (params.ad_zone_identical != -1) :
                url += "&ad_zone="
                url += str(params.ad_zone_prefix)
                if params.ad_zone_identical==0:
                    url += str(i+1)
                elif  params.ad_zone_identical==1:
                    url += str(1)
                elif  params.ad_zone_identical==2:
                    pass
        bw_layers_for_channel = layers_bw_list[int(i%len(layers_bw_list))]
        num_of_layers_list = [float(k) for k in bw_layers_for_channel.split(',')]
        url += "&bandwidth="
        url += str((num_of_layers_list[0]*1024.*1024.)) 
        url += str("&size=0&live=1")
        url += "&monitor=" + str(params.monitor)
        url += str("&source_addr=" + urllib.quote_plus(params.source_addr))              
        url += "&size=" + str(len(num_of_layers_list))
        
        for j in range (len(num_of_layers_list)):
            url += "&live_feed_address=" + str(params.multicast_addr)
            url += urllib.quote_plus(":")
            url += str(orig_port)
            url += "&bandwidth=" + str((num_of_layers_list[j])*1024.*1024.)
            orig_port += 1
        orig_port = params.start_port
        url += str("&vbr=1") 
        print "*********" , url
        url_result = urllib2.urlopen(url)
        print "ABR Channel number %d : name -> %s, MultiCast address -> %s, first port -> %s, num of layers -> %s \n" % (int(i + 1), str(channel_name) , str(params.multicast_addr), str(params.start_port),str(len(num_of_layers_list)))                
        #if params.one_fake_machine == 1: # sending to incremental fake port
        #    params.start_port += 1        
        #else : # Sending to incremental IP
        fake_IP_nums = stb_ip_parse(params.multicast_addr)
        #print fake_IP_nums
        if fake_IP_nums[3] > 253:
            fake_IP_nums[3] = 0
            fake_IP_nums[2] += 1 
                            
        #re-assemble the fake ip string           
        fake_IP_nums[3] = int(fake_IP_nums[3])
        fake_IP_nums[3] += 1
        params.multicast_addr = str_stb_ip_parse(fake_IP_nums)
        channel_name = "%s%s" % (params.channel_prefix,str(i))

           
           
           
                                         
    return channels







def UpdateEncodingProfileCBR():
    global params,enc_array
    cbr_enc_id = []    
    layers_bw_list = params.cbr_layers_bw.split(',')
    manager_ip = params.manager[:string.find(params.manager,":")]
    manager_port = int(params.manager[string.find(params.manager,":") + 1:])
    url = "http://%s/get_encoding_profiles?X=0" % (str(params.manager))
    EncodingProfileResult = urllib2.urlopen(url)
    xml_EncodingProfile = EncodingProfileResult.read()
    parse_EncodingProfile = libxml2.parseDoc(xml_EncodingProfile)
    #print parse_EncodingProfile
    list = parse_EncodingProfile.xpathEval("//X/value/profiles/elem/bandwidth")
    EncProfExist = 0
    VideoMPG2EncExist = 0
    VideoH264EncExist = 0
    msg=''
    if params.is_abr_channel == 1 or params.is_abr_channel == 2 or params.is_abr_channel == 3:
        for j in range(len(layers_bw_list)):
            for url in list:
                print url.content
                #print url.content                
#                if int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 1000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 1000):
#                     EncProfExist = 1    
                try:            
                    if str(url.next.next.next.next.name).find("mpeg2") != -1 and  enc_array[j%len(layers_bw_list)] == 'mpg2' and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 50000):
                         VideoMPG2EncExist = 1
                         EncProfExist = 1
                    if str(url.next.next.next.next.name).find("h264") != -1 and enc_array[j%len(layers_bw_list)] == 'mpg4' and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 50000):
                         VideoH264EncExist = 1
                         EncProfExist = 1
                    if enc_array[j%len(layers_bw_list)] == '' and EncProfExist == 1 and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 50000):
                         EncProfExist = 1
                except:
                    pass
            if (EncProfExist == 1 and VideoMPG2EncExist == 1 and enc_array[j%len(layers_bw_list)] == 'mpg2') :          
                EncProfExist = 0;
                VideoMPG2EncExist = 0;
            elif (EncProfExist == 1 and VideoH264EncExist == 1 and enc_array[j%len(layers_bw_list)] == 'mpg4') :          
                EncProfExist = 0;
                VideoH264EncExist = 0;
            elif (EncProfExist == 1 and enc_array[0] == '') :
                EncProfExist = 0;        
            elif (EncProfExist == 0 and enc_array[0] == '' or (EncProfExist == 0 and enc_array[0] != '' and (params.is_abr_channel == 1 or params.is_abr_channel == 2))) :
                msg ='''<X>
  <profile>
    <enc_id>0</enc_id>
    <bandwidth>%s</bandwidth>    
    <name>%s</name>
  </profile>
</X>'''    % (str(int(float(layers_bw_list[j])*1048576)),str(layers_bw_list[j]))
            elif (EncProfExist == 1 and VideoH264EncExist == 0 and enc_array[j%len(layers_bw_list)] == 'mpg4') or (EncProfExist == 0 and VideoH264EncExist == 1 and enc_array[j%len(layers_bw_list)] == 'mpg4') or (EncProfExist == 0 and VideoH264EncExist == 0 and enc_array[j%len(layers_bw_list)] == 'mpg4'):
                msg='''<X>
  <profile>
    <enc_id>0</enc_id>
    <bandwidth>%s</bandwidth>
    <name>h264_%s</name>
    <overhead_bandwidth>0</overhead_bandwidth>
    <h264_video_settings>
      <h264_video_format>
        <def_horizontal_size>352</def_horizontal_size>
        <def_vertical_size>240</def_vertical_size>
        <frame_rate>29.97</frame_rate>
        <interlace_mode>0</interlace_mode>
        <field_order>0</field_order>
        <video_pulldown_flag>0</video_pulldown_flag>
        <chroma_format>1</chroma_format>
        <bit_depth_luma>8</bit_depth_luma>
        <bit_depth_chroma>8</bit_depth_chroma>
        <video_format>2</video_format>
        <sar_width>0</sar_width>
        <sar_height>0</sar_height>
      </h264_video_format>
      <h264_bitrate>
        <bit_rate_mode>0</bit_rate_mode>
        <bit_rate>%s</bit_rate>
        <max_bit_rate>3145728</max_bit_rate>
        <vbv_buffer_units>0</vbv_buffer_units>
        <bit_rate_buffer_size>0</bit_rate_buffer_size>
        <vbv_buffer_fullness>10</vbv_buffer_fullness>
        <vbv_buffer_fullness_trg>100</vbv_buffer_fullness_trg>
        <hrd_maintain>1</hrd_maintain>
        <max_frame_size_I>0</max_frame_size_I>
        <max_frame_size_P>0</max_frame_size_P>
        <max_frame_size_B>0</max_frame_size_B>
        <max_frame_size_Br>0</max_frame_size_Br>
      </h264_bitrate>
      <h264_profile>
        <profile_id>1</profile_id>
        <level_id>100</level_id>
      </h264_profile>
      <h264_gop_structure>
        <vcsd_mode>1</vcsd_mode>
        <idr_interval>33</idr_interval>
        <reordering_delay>4</reordering_delay>
        <idr_frequency>1</idr_frequency>
        <fixed_i_position>0</fixed_i_position>
        <adaptive_b_frames>1</adaptive_b_frames>
        <b_slice_pyramid>0</b_slice_pyramid>
        <b_slice_reference>0</b_slice_reference>
      </h264_gop_structure>
      <h264_motion_estimation>
        <inter_search_shape>0</inter_search_shape>
        <me_subpel_mode>0</me_subpel_mode>
        <num_reference_frames>3</num_reference_frames>
        <search_range>72</search_range>
        <me_weighted_p_mode>1</me_weighted_p_mode>
        <fast_multi_ref_me>1</fast_multi_ref_me>
        <fast_sub_block_me>1</fast_sub_block_me>
      </h264_motion_estimation>
      <h264_rate_distortion>
        <enable_fast_intra_decisions>1</enable_fast_intra_decisions>
        <enable_fast_inter_decisions>1</enable_fast_inter_decisions>
        <fast_rd_optimization>1</fast_rd_optimization>
        <use_hadamard_transform>0</use_hadamard_transform>
        <adaptive_quant_strength_brightness>0</adaptive_quant_strength_brightness>
        <adaptive_quant_strength_contrast>0</adaptive_quant_strength_contrast>
        <adaptive_quant_strength_complexity>0</adaptive_quant_strength_complexity>
      </h264_rate_distortion>
      <h264_misc>
        <use_deblocking_filter>1</use_deblocking_filter>
        <deblocking_alphaC0_offset>-1</deblocking_alphaC0_offset>
        <deblocking_beta_offset>-1</deblocking_beta_offset>
        <entropy_coding_mode>1</entropy_coding_mode>
        <num_threads>0</num_threads>
        <encoding_pass_count>1</encoding_pass_count>
      </h264_misc>
    </h264_video_settings>
    <video_type>1</video_type>
    <read_only>0</read_only>
  </profile>
  <validate>0</validate>
</X>'''   % (str(int(float(layers_bw_list[j])*1048576)),str(layers_bw_list[j]),str(int(float(layers_bw_list[j])*1048576)))

            elif (EncProfExist == 1 and VideoMPG2EncExist == 0 and enc_array[j%len(layers_bw_list)] == 'mpg2') or (EncProfExist == 0 and VideoMPG2EncExist == 1 and enc_array[j%len(layers_bw_list)] == 'mpg2') or (EncProfExist == 0 and VideoMPG2EncExist == 0 and enc_array[j%len(layers_bw_list)] == 'mpg2'):    
                msg='''<X>
  <profile>
    <enc_id>0</enc_id>
    <bandwidth>%s</bandwidth>
    <name>mpg2_%s</name>
    <overhead_bandwidth>0</overhead_bandwidth>
    <mpeg2_video_settings>
      <mpeg2_video_format>
        <video_pulldown_flag>0</video_pulldown_flag>
        <def_horizontal_size>352</def_horizontal_size>
        <def_vertical_size>240</def_vertical_size>
        <frame_rate_code>0</frame_rate_code>
        <deinterlacing_mode>0</deinterlacing_mode>
        <video_format>2</video_format>
        <aspectratio>0</aspectratio>
        <features_flags>2048</features_flags>
        <write_sh>1</write_sh>
        <write_sec>1</write_sec>
        <prog_seq>0</prog_seq>
        <prog_frame>1</prog_frame>
        <topfirst>1</topfirst>
        <dc_prec>1</dc_prec>
      </mpeg2_video_format>
      <mpeg2_bitrate>
        <bit_rate_mode>0</bit_rate_mode>
        <bit_rate>%s</bit_rate>
        <max_bit_rate>3145728</max_bit_rate>
        <avg_bit_rate>3110000</avg_bit_rate>
        <min_bit_rate>1874250</min_bit_rate>
        <mquant_value>10</mquant_value>
        <mquant_limit>0</mquant_limit>
        <vbv_buffer_size>0</vbv_buffer_size>
        <fixed_vbv_delay>1</fixed_vbv_delay>
      </mpeg2_bitrate>
      <mpeg2_profile>
        <profile_id>4</profile_id>
        <level_id>4</level_id>
      </mpeg2_profile>
      <mpeg2_gop_structure>
        <t_N>16</t_N>
        <min_N>16</min_N>
        <M>3</M>
        <closed_gop_interval>0</closed_gop_interval>
      </mpeg2_gop_structure>
      <mpeg2_motion_estimation>
        <motion_search_type>17</motion_search_type>
      </mpeg2_motion_estimation>
    </mpeg2_video_settings>
    <video_type>2</video_type>
    <read_only>0</read_only>
  </profile>
  <validate>0</validate>
</X>''' % (str(int(float(layers_bw_list[j])*1048576)),str(layers_bw_list[j]),str(int(float(layers_bw_list[j])*1048576)))

            if msg!='':
                msg_len  = len(msg)
#                msg_header = '''POST /add_encoding_profile HTTP/1.1
#    User-Agent: Jakarta Commons-HttpClient/3.1
#    Host: %s
#    Content-Length: %s
#    Content-Type: text/xml; charset=utf-8
    
#    ''' % (str(params.manager),str(msg_len))
                msg_header = '''POST /add_encoding_profile HTTP/1.1
Content-Length: %s
Content-Type: text/xml; charset=UTF-8
Host: %s
Connection: Keep-Alive
User-Agent: Apache-HttpClient/4.2.5 (java 1.5)

'''   % (str(msg_len),str(params.manager))
    
                #print msg_header + msg
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((manager_ip,manager_port ))   
                s.send(msg_header)
                s.sendall(msg)
                datarecv=s.recv(1024)
                print "Reply Received: "+ str(datarecv)
                msg=''
                msg_header=''
    if  params.is_abr_channel == 0 :
            for url in list:
                #print url.content                
                #if int(float(params.bandwidth)*1048576) >= (int(url.content) - 1000) and int(float(params.bandwidth)*1048576) <= (int(url.content) + 1000):
                if int(float(layers_bw_list[0])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[0])*1048576) <= (int(url.content) + 50000):
                    EncProfExist = 1
                else:
                    pass
            if EncProfExist == 1:            
                EncProfExist = 0
            else:            
                msg = '''<X>
  <profile>
    <enc_id>0</enc_id>
    <bandwidth>%s</bandwidth>
    <overhead_bandwidth>100000</overhead_bandwidth>
    <name>%s</name>
  </profile>
</X>''' % (str(int(float(layers_bw_list[0])*1048576)),str(layers_bw_list[0]))
#                msg = '''<X>
#  <profile>
#    <enc_id>0</enc_id>
#    <bandwidth>%s</bandwidth>
#    <overhead_bandwidth>100000</overhead_bandwidth>
#    <name>%s</name>
#  </profile>
#</X>''' % (str(int(float(params.bandwidth)*1048576)),str(params.bandwidth))
    
    
                msg_len  = len(msg)
                msg_header = '''POST /add_encoding_profile HTTP/1.1
User-Agent: Jakarta Commons-HttpClient/3.1
Host: %s
Content-Length: %s
Content-Type: text/xml; charset=utf-8

''' % (str(params.manager),str(msg_len))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((manager_ip,manager_port ))   
                s.send(msg_header)
                s.sendall(msg)
                datarecv=s.recv(1024)
                #print "Reply Received: "+ str(datarecv)
                msg=''    

    
    url = "http://%s/get_encoding_profiles?X=0" % (str(params.manager))
    EncodingProfileResult = urllib2.urlopen(url)
    xml_EncodingProfile = EncodingProfileResult.read()
    parse_EncodingProfile = libxml2.parseDoc(xml_EncodingProfile)
    #print parse_EncodingProfile
    list = parse_EncodingProfile.xpathEval("//X/value/profiles/elem/bandwidth")
    if(params.is_abr_channel == 0):
        for url in list:
            #print url.content                
            if int(float(layers_bw_list[0])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[0])*1048576) <= (int(url.content) + 50000):
                cbr_enc_id.append(url.prev.prev.content)
            else:
                pass
        #print enc_id
       
    if (params.is_abr_channel == 2 or params.is_abr_channel == 1):
        for j in range(len(layers_bw_list)):
            for url in list:
                #print url.content                
                #if int(float(layers_bw_list[j])*1000000) >= (int(url.content) - 50000) and int(float(layers_bw_list[j])*1000000) <= (int(url.content) + 50000):
                if int(float(layers_bw_list[j])*1000000) >= (int(url.content) - 0.1*int(url.content)) and int(float(layers_bw_list[j])*1000000) <= (int(url.content) + 0.1*int(url.content)):
                    cbr_enc_id.append(url.prev.prev.content)
                else:
                    pass
    if (params.is_abr_channel == 3):
        for j in range(len(layers_bw_list)):
            for url in list:
                try:
                    if str(url.next.next.next.next.name).find("mpeg2") != -1 and  enc_array[j%len(layers_bw_list)] == 'mpg2' and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 50000):
                         cbr_enc_id.append(url.prev.prev.content)
                    if str(url.next.next.next.next.name).find("h264") != -1 and enc_array[j%len(layers_bw_list)] == 'mpg4' and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 50000):
                        cbr_enc_id.append(url.prev.prev.content)
                    if enc_array[j%len(layers_bw_list)] == '' and EncProfExist == 1 and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 50000):
                         cbr_enc_id.append(url.prev.prev.content)
                except:
                    pass     
        #print cbr_enc_id 
    
    
       
    return cbr_enc_id















def UpdateEncodingProfile():
    global params,enc_array
    enc_id = []
    layers_bw_list = params.layers_bw.split(',')
    cbr_layers_bw_list = params.cbr_layers_bw.split(',')
    manager_ip = params.manager[:string.find(params.manager,":")]
    manager_port = int(params.manager[string.find(params.manager,":") + 1:])
    url = "http://%s/get_encoding_profiles?X=0" % (str(params.manager))
    EncodingProfileResult = urllib2.urlopen(url)    
    xml_EncodingProfile = EncodingProfileResult.read()
    print xml_EncodingProfile
    parse_EncodingProfile = libxml2.parseDoc(xml_EncodingProfile)
    #print parse_EncodingProfile
    list = parse_EncodingProfile.xpathEval("//X/value/profiles/elem/bandwidth")
    EncProfExist = 0
    VideoMPG2EncExist = 0
    VideoH264EncExist = 0
    msg=''
    if params.is_abr_channel == 1 or params.is_abr_channel == 2 or params.is_abr_channel == 3:
        for j in range(len(layers_bw_list)):
            for url in list:
                #print url.content                
#                if int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 1000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 1000):
#                     EncProfExist = 1    
                try:            
                    if str(url.next.next.next.next.name).find("mpeg2") != -1 and  enc_array[j%len(layers_bw_list)] == 'mpg2' and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 20000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 20000):
                         VideoMPG2EncExist = 1
                         EncProfExist = 1
                    if str(url.next.next.next.next.name).find("h264") != -1 and enc_array[j%len(layers_bw_list)] == 'mpg4' and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 20000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 20000):
                         VideoH264EncExist = 1
                         EncProfExist = 1
#                    if enc_array[j%len(layers_bw_list)] == '' and EncProfExist == 0 and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 50000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 50000):
                    if enc_array[0] == '' and EncProfExist == 0 and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 20000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 20000):
                         EncProfExist = 1
                except:
                    pass
            if (EncProfExist == 1 and VideoMPG2EncExist == 1 and enc_array[j%len(layers_bw_list)] == 'mpg2') :          
                EncProfExist = 0;
                VideoMPG2EncExist = 0;
            elif (EncProfExist == 1 and VideoH264EncExist == 1 and enc_array[j%len(layers_bw_list)] == 'mpg4') :          
                EncProfExist = 0;
                VideoH264EncExist = 0;
            elif (EncProfExist == 1 and enc_array[0] == '') :
                EncProfExist = 0;        
            elif (EncProfExist == 0 and enc_array[0] == '' or (EncProfExist == 0 and enc_array[0] != '' and (params.is_abr_channel == 1 or params.is_abr_channel == 2))) :
                msg ='''<X>
  <profile>
    <enc_id>0</enc_id>
    <bandwidth>%s</bandwidth>    
    <name>%s</name>
  </profile>
</X>'''    % (str(int(float(layers_bw_list[j])*1048576)),str(layers_bw_list[j]))
            elif (EncProfExist == 1 and VideoH264EncExist == 0 and enc_array[j%len(layers_bw_list)] == 'mpg4') or (EncProfExist == 0 and VideoH264EncExist == 1 and enc_array[j%len(layers_bw_list)] == 'mpg4') or (EncProfExist == 0 and VideoH264EncExist == 0 and enc_array[j%len(layers_bw_list)] == 'mpg4'):
                msg='''<X>
  <profile>
    <enc_id>0</enc_id>
    <bandwidth>%s</bandwidth>
    <name>h264_%s</name>
    <overhead_bandwidth>0</overhead_bandwidth>
    <h264_video_settings>
      <h264_video_format>
        <def_horizontal_size>352</def_horizontal_size>
        <def_vertical_size>240</def_vertical_size>
        <frame_rate>29.97</frame_rate>
        <interlace_mode>0</interlace_mode>
        <field_order>0</field_order>
        <video_pulldown_flag>0</video_pulldown_flag>
        <chroma_format>1</chroma_format>
        <bit_depth_luma>8</bit_depth_luma>
        <bit_depth_chroma>8</bit_depth_chroma>
        <video_format>2</video_format>
        <sar_width>0</sar_width>
        <sar_height>0</sar_height>
      </h264_video_format>
      <h264_bitrate>
        <bit_rate_mode>0</bit_rate_mode>
        <bit_rate>%s</bit_rate>
        <max_bit_rate>3145728</max_bit_rate>
        <vbv_buffer_units>0</vbv_buffer_units>
        <bit_rate_buffer_size>0</bit_rate_buffer_size>
        <vbv_buffer_fullness>10</vbv_buffer_fullness>
        <vbv_buffer_fullness_trg>100</vbv_buffer_fullness_trg>
        <hrd_maintain>1</hrd_maintain>
        <max_frame_size_I>0</max_frame_size_I>
        <max_frame_size_P>0</max_frame_size_P>
        <max_frame_size_B>0</max_frame_size_B>
        <max_frame_size_Br>0</max_frame_size_Br>
      </h264_bitrate>
      <h264_profile>
        <profile_id>1</profile_id>
        <level_id>100</level_id>
      </h264_profile>
      <h264_gop_structure>
        <vcsd_mode>1</vcsd_mode>
        <idr_interval>33</idr_interval>
        <reordering_delay>4</reordering_delay>
        <idr_frequency>1</idr_frequency>
        <fixed_i_position>0</fixed_i_position>
        <adaptive_b_frames>1</adaptive_b_frames>
        <b_slice_pyramid>0</b_slice_pyramid>
        <b_slice_reference>0</b_slice_reference>
      </h264_gop_structure>
      <h264_motion_estimation>
        <inter_search_shape>0</inter_search_shape>
        <me_subpel_mode>0</me_subpel_mode>
        <num_reference_frames>3</num_reference_frames>
        <search_range>72</search_range>
        <me_weighted_p_mode>1</me_weighted_p_mode>
        <fast_multi_ref_me>1</fast_multi_ref_me>
        <fast_sub_block_me>1</fast_sub_block_me>
      </h264_motion_estimation>
      <h264_rate_distortion>
        <enable_fast_intra_decisions>1</enable_fast_intra_decisions>
        <enable_fast_inter_decisions>1</enable_fast_inter_decisions>
        <fast_rd_optimization>1</fast_rd_optimization>
        <use_hadamard_transform>0</use_hadamard_transform>
        <adaptive_quant_strength_brightness>0</adaptive_quant_strength_brightness>
        <adaptive_quant_strength_contrast>0</adaptive_quant_strength_contrast>
        <adaptive_quant_strength_complexity>0</adaptive_quant_strength_complexity>
      </h264_rate_distortion>
      <h264_misc>
        <use_deblocking_filter>1</use_deblocking_filter>
        <deblocking_alphaC0_offset>-1</deblocking_alphaC0_offset>
        <deblocking_beta_offset>-1</deblocking_beta_offset>
        <entropy_coding_mode>1</entropy_coding_mode>
        <num_threads>0</num_threads>
        <encoding_pass_count>1</encoding_pass_count>
      </h264_misc>
    </h264_video_settings>
    <video_type>1</video_type>
    <read_only>0</read_only>
  </profile>
  <validate>0</validate>
</X>'''   % (str(int(float(layers_bw_list[j])*1048576)),str(layers_bw_list[j]),str(int(float(layers_bw_list[j])*1048576)))

            elif (EncProfExist == 1 and VideoMPG2EncExist == 0 and enc_array[j%len(layers_bw_list)] == 'mpg2') or (EncProfExist == 0 and VideoMPG2EncExist == 1 and enc_array[j%len(layers_bw_list)] == 'mpg2') or (EncProfExist == 0 and VideoMPG2EncExist == 0 and enc_array[j%len(layers_bw_list)] == 'mpg2'):    
                msg='''<X>
  <profile>
    <enc_id>0</enc_id>
    <bandwidth>%s</bandwidth>
    <name>mpg2_%s</name>
    <overhead_bandwidth>0</overhead_bandwidth>
    <mpeg2_video_settings>
      <mpeg2_video_format>
        <video_pulldown_flag>0</video_pulldown_flag>
        <def_horizontal_size>352</def_horizontal_size>
        <def_vertical_size>240</def_vertical_size>
        <frame_rate_code>0</frame_rate_code>
        <deinterlacing_mode>0</deinterlacing_mode>
        <video_format>2</video_format>
        <aspectratio>0</aspectratio>
        <features_flags>2048</features_flags>
        <write_sh>1</write_sh>
        <write_sec>1</write_sec>
        <prog_seq>0</prog_seq>
        <prog_frame>1</prog_frame>
        <topfirst>1</topfirst>
        <dc_prec>1</dc_prec>
      </mpeg2_video_format>
      <mpeg2_bitrate>
        <bit_rate_mode>0</bit_rate_mode>
        <bit_rate>%s</bit_rate>
        <max_bit_rate>3145728</max_bit_rate>
        <avg_bit_rate>45000000</avg_bit_rate>
        <min_bit_rate>1874250</min_bit_rate>
        <mquant_value>10</mquant_value>
        <mquant_limit>0</mquant_limit>
        <vbv_buffer_size>0</vbv_buffer_size>
        <fixed_vbv_delay>1</fixed_vbv_delay>
      </mpeg2_bitrate>
      <mpeg2_profile>
        <profile_id>4</profile_id>
        <level_id>4</level_id>
      </mpeg2_profile>
      <mpeg2_gop_structure>
        <t_N>16</t_N>
        <min_N>16</min_N>
        <M>3</M>
        <closed_gop_interval>0</closed_gop_interval>
      </mpeg2_gop_structure>
      <mpeg2_motion_estimation>
        <motion_search_type>17</motion_search_type>
      </mpeg2_motion_estimation>
    </mpeg2_video_settings>
    <video_type>2</video_type>
    <read_only>0</read_only>
  </profile>
  <validate>0</validate>
</X>''' % (str(int(float(layers_bw_list[j])*1048576)),str(layers_bw_list[j]),str(int(float(layers_bw_list[j])*1048576)))

            if msg!='':
                msg_len  = len(msg)
#                msg_header = '''POST /add_encoding_profile HTTP/1.1
#    User-Agent: Jakarta Commons-HttpClient/3.1
#    Host: %s
#    Content-Length: %s
#    Content-Type: text/xml; charset=utf-8
    
#    ''' % (str(params.manager),str(msg_len))
                msg_header = '''POST /add_encoding_profile HTTP/1.1
Content-Length: %s
Content-Type: text/xml; charset=UTF-8
Host: %s
Connection: Keep-Alive
User-Agent: Apache-HttpClient/4.2.5 (java 1.5)

'''   % (str(msg_len),str(params.manager))
    
                #print msg_header + msg
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((manager_ip,manager_port ))   
                s.send(msg_header)
                s.sendall(msg)
                datarecv=s.recv(1024)
                #print "Reply Received: "+ str(datarecv)
                msg=''
                msg_header=''
    if  params.is_abr_channel == 0 :
            for url in list:
                #print url.content                
                if int(float(cbr_layers_bw_list[0])*1048576) >= (int(url.content) - 50000) and int(float(cbr_layers_bw_list[0])*1048576) <= (int(url.content) + 50000):
                    EncProfExist = 1
                else:
                    pass
            if EncProfExist == 1:            
                EncProfExist = 0
            else:            
                msg = '''<X>
  <profile>
    <enc_id>0</enc_id>
    <bandwidth>%s</bandwidth>
    <overhead_bandwidth>100000</overhead_bandwidth>
    <name>%s</name>
  </profile>
</X>''' % (str(int(float(cbr_layers_bw_list[0])*1048576)),str(cbr_layers_bw_list[0]))
#                msg = '''<X>
#  <profile>
#    <enc_id>0</enc_id>
#    <bandwidth>%s</bandwidth>
#    <overhead_bandwidth>100000</overhead_bandwidth>
#    <name>%s</name>
#  </profile>
#</X>''' % (str(int(float(params.bandwidth)*1048576)),str(params.bandwidth))
    
    
                msg_len  = len(msg)
                msg_header = '''POST /add_encoding_profile HTTP/1.1
User-Agent: Jakarta Commons-HttpClient/3.1
Host: %s
Content-Length: %s
Content-Type: text/xml; charset=utf-8

''' % (str(params.manager),str(msg_len))
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((manager_ip,manager_port ))   
                s.send(msg_header)
                s.sendall(msg)
                datarecv=s.recv(1024)
                #print "Reply Received: "+ str(datarecv)
                msg=''    

    
    url = "http://%s/get_encoding_profiles?X=0" % (str(params.manager))
    EncodingProfileResult = urllib2.urlopen(url)
    xml_EncodingProfile = EncodingProfileResult.read()
    parse_EncodingProfile = libxml2.parseDoc(xml_EncodingProfile)
    #print parse_EncodingProfile
    list = parse_EncodingProfile.xpathEval("//X/value/profiles/elem/bandwidth")
    if(params.is_abr_channel == 0):
        for url in list:
            #print url.content                
            if int(float(cbr_layers_bw_list[0])*1048576) >= (int(url.content) - 20000) and int(float(cbr_layers_bw_list[0])*1048576) <= (int(url.content) + 20000):
                enc_id.append(url.prev.prev.content)
            else:
                pass
        #print enc_id
       
    if (params.is_abr_channel == 2 or params.is_abr_channel == 1):
        for j in range(len(layers_bw_list)):
            for url in list:
                #print url.content                
                #if int(float(layers_bw_list[j])*1000000) >= (int(url.content) - 30000) and int(float(layers_bw_list[j])*1000000) <= (int(url.content) + 30000):
                if int(float(layers_bw_list[j])*1000000) >= (int(url.content) - 0.1*int(url.content)) and int(float(layers_bw_list[j])*1000000) <= (int(url.content) + 0.1*int(url.content)):
                    enc_id.append(url.prev.prev.content)
                else:
                    pass
    if (params.is_abr_channel == 3):
        for j in range(len(layers_bw_list)):
            for url in list:
                try:
                    if str(url.next.next.next.next.name).find("mpeg2") != -1 and  enc_array[j%len(layers_bw_list)] == 'mpg2' and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 20000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 20000):
                         enc_id.append(url.prev.prev.content)
                    if str(url.next.next.next.next.name).find("h264") != -1 and enc_array[j%len(layers_bw_list)] == 'mpg4' and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 20000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 20000):
                        enc_id.append(url.prev.prev.content)
                    if enc_array[j%len(layers_bw_list)] == '' and EncProfExist == 1 and int(float(layers_bw_list[j])*1048576) >= (int(url.content) - 20000) and int(float(layers_bw_list[j])*1048576) <= (int(url.content) + 20000):
                         enc_id.append(url.prev.prev.content)
                except:
                    pass     
        #print enc_id 
    
    
       
    return enc_id

def channel_name_id():
    global params
    global channels_name_id_dictionary
    url = "http://%s/multicast_channel/get_all?offset=0&limit=10000" % (params.manager)
    all_channels = urllib2.urlopen(url)
    xml = all_channels.read()
    xml_obj = ET.fromstring(xml)
    channels_list = libxml2.parseDoc(xml)
    xpath="//X/value/total"       
    list = channels_list.xpathEval(xpath)
    for node in list:
        print "Total Channel in System = %s" %  str(node.content)
    
    for x in xml_obj.findall('./value/channels/elem'):
        id = x.find('./id').text
        name = x.find('./name').text
        print id, name
        channels_name_id_dictionary[str(name)] = str(id)
    
    
 
def addChannelCbrSeveralMulticast():
    global params, cbr_multicast_array,cbr_port_array
    global channels_name_id_dictionary
    enc_id = UpdateEncodingProfile()
    layers_bw_list = params.layers_bw.split(',')
    orig_port = params.start_port
    manager_ip = params.manager[:string.find(params.manager,":")]
    manager_port = int(params.manager[string.find(params.manager,":") + 1:])
    ad_zone_sufix = 0
    if (params.update_channels == 1):
        channel_name_id()
        
    for i in range (params.num_channel_map):
        if (params.update_channels == 1):
            name = "%s%s" % (str(params.channel_prefix),str(i))
            id = channels_name_id_dictionary[str(name)]
            update=1
        else:
            update=0
            id=0
        if params.ad_zone_identical==0:
            ad_zone_sufix += int(i+1)
        elif  params.ad_zone_identical==1:
            ad_zone_sufix = 1
        elif  params.ad_zone_identical==2:
            ad_zone_sufix = str('')
            
        msg1='''<X>
    <update>%s</update>
    <channel>
        <name>%s%s</name>
        <id>%s</id>
        <ad_zone>%s%s</ad_zone>
        <monitor>%s</monitor>
        <abr>
            <live>0</live>
            <vbr>0</vbr>
            <edge_id>0</edge_id>  
        </abr>
        <alias></alias>
        <original_pid>0</original_pid>
        <cbr_live>0</cbr_live>
        <cbr_edge_id>0</cbr_edge_id>''' %  (str(update),str(params.channel_prefix),str(i),str(id), str(params.ad_zone_prefix),str(ad_zone_sufix),str(params.monitor))
        
        msg3 = ''
        for j in range(len(layers_bw_list)):
                msg2 ='''<cbr_sources>
            <addr>%s:%s</addr>
            <encoding_profile>%s</encoding_profile>
        </cbr_sources>''' % (str(cbr_multicast_array[j%len(cbr_multicast_array)]),str(cbr_port_array[j%len(cbr_port_array)]),str(enc_id[j]))
                #orig_port += 1
                msg3 += msg2
    
        msg4='''
    </channel>
</X>'''
        if (params.only_one_multicast == 0 ):
                if params.one_fake_machine == 1: # sending to incremental fake port
                    #params.start_port += 1
                    for i in range(len(cbr_port_array)):                        
                       tmp_port= int(cbr_port_array[i])
                       tmp_port += 1
                       cbr_port_array[i] = tmp_port
                else : # Sending to incremental IP
                    for i in range(len(cbr_multicast_array)):
                        fake_IP_nums = stb_ip_parse(cbr_multicast_array[i])
                        #print fake_IP_nums
                        if fake_IP_nums[3] > 253:
                            fake_IP_nums[3] = 0
                            fake_IP_nums[2] += 1 
                                            
                        #re-assemble the fake ip string           
                        fake_IP_nums[3] = int(fake_IP_nums[3])
                        fake_IP_nums[3] += 1
                        cbr_multicast_array[i] = str_stb_ip_parse(fake_IP_nums)
        else:
                pass    
            
            
            
            
            
            
            
            
            
            
            
            
        msg =  msg1 + msg3 + msg4
        print str(msg)
        msg_len  = len(msg)
        msg_header = '''POST /multicast_channel/update HTTP/1.1
Content-Length: %s
Content-Type: text/x-xml2
Host: %s
Connection: Keep-Alive
User-Agent: Apache-HttpClient/4.2.5 (java 1.5)

''' % (str(msg_len),str(params.manager))

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((manager_ip,int(manager_port) )) 
        s.send(msg_header)
        s.sendall(msg)
        print str(msg_header) + str(msg)
        datarecv=s.recv(1024)
        print "Reply Received: "+ str(datarecv)
        if (params.is_abr_channel == 3):
            if (params.only_one_multicast == 0 ):
                fake_IP_nums = stb_ip_parse(params.multicast_addr)
                #print fake_IP_nums
                if fake_IP_nums[3] > 253:
                    fake_IP_nums[3] = 0
                    fake_IP_nums[2] += 1 
                                    
                #re-assemble the fake ip string           
                fake_IP_nums[3] = int(fake_IP_nums[3])
                fake_IP_nums[3] += 1
                params.multicast_addr = str_stb_ip_parse(fake_IP_nums)
                orig_port = params.start_port
            else:
                orig_port = params.start_port                

            
        
def addChannelEncdingProfileXML5():
    global params ,cbr_multicast_array,cbr_port_array
    global channels_name_id_dictionary
    enc_id = UpdateEncodingProfile()
    cbr_enc_id = UpdateEncodingProfileCBR()
    layers_bw_list = params.layers_bw.split(',')
    cbr_layers_bw_list = params.cbr_layers_bw.split(',')
    orig_port = params.start_port
    manager_ip = params.manager[:string.find(params.manager,":")]
    manager_port = int(params.manager[string.find(params.manager,":") + 1:])
    ad_zone_sufix = 0
    
    pods_array = params.pods_ids.split(';')
    
    objs = "RS"
    pods_percentage_array = map(int, params.pods_dist_to_chnl.split(';'))   
    pods_counter = [0] * len(pods_array)
    
    #freqs = [int(cfg.ff_percent),int(cfg.rew_percent),int(cfg.pause_percent)]        
    wc = wchoice(pods_array, pods_percentage_array, filter=False)
    
    channel_by_pods = [wc() for _ in xrange(params.num_channel_map)]
    
    
    if (params.update_channels == 1):
        channel_name_id()
        
    for i in range (params.num_channel_map):
        if(params.use_edge_ids == 1):
            edge_id=str(channel_by_pods[i%params.num_channel_map])
        else:
            edge_id='0'
        
        if (params.update_channels == 1):
            name = "%s%s" % (str(params.channel_prefix),str(i))
            id = channels_name_id_dictionary[str(name)]
            update=1
        else:
            update=0
            id=0
            
        msg1='''<X>
    <update>%s</update>
    <channel>
        <name>%s%s</name>
        <id>%s</id>''' % (str(update),str(params.channel_prefix),str(i),str(id))
        if params.ad_zone_identical==0:
            ad_zone_sufix += int(i+1)
        elif  params.ad_zone_identical==1:
            ad_zone_sufix = 1
        elif  params.ad_zone_identical==2:
            ad_zone_sufix = str('')
        msg2 = '''
        <ad_zone>%s%s</ad_zone>''' % (str(params.ad_zone_prefix),str(ad_zone_sufix))
        if params.ad_zone_identical== -1:
            msg2 = '''
        <ad_zone></ad_zone>'''
        
        msg3='''
        <monitor>%s</monitor>'''  % (str(params.monitor))
        if params.abr_live == 1:
            msg4='''
        <abr>
            <live>1</live>
            ''' 
        else:
            msg4='''
        <abr>
            <live>0</live>
            '''       
        
        msg6 = ''
        if(params.is_abr_channel == 1 or params.is_abr_channel == 2):
            for j in range(len(layers_bw_list)):
                msg5 = '''<layers>
                <live_feed_address>%s:%s</live_feed_address>
                <encoding_profile>%s</encoding_profile>
            </layers>
            ''' % (str(params.multicast_addr),str(orig_port),str(enc_id[j]))
                orig_port += 1
                msg6 += msg5
        
        if str(params.source_addr) != '':
            msg7=    '''<vbr>1</vbr>
                <source_addrs>%s:0</source_addrs>
                <edge_id>%s</edge_id>
                <live_pause>%s</live_pause>
            </abr>
            <alias></alias>
            <original_pid>0</original_pid>''' % (str(params.source_addr),str(edge_id),str(params.pause))
        else:
             msg7=    '''<vbr>1</vbr>
                <edge_id>%s</edge_id>
            </abr>
            <alias></alias>
            <original_pid>0</original_pid>''' % (str(edge_id))           
        msg8 = '''
        <cbr_live>%s</cbr_live>
        <cbr_edge_id>%s</cbr_edge_id>''' % (str(params.cbr_live),str(edge_id))
        
        msg9 = ''
#        if(params.is_abr_channel == 1 or params.is_abr_channel == 2):
        if(params.is_abr_channel == 2):
            for j in range(len(cbr_layers_bw_list)):
                if params.cbr_igmp_source_addr == '':
                    msg10 = '''
            <cbr_sources>
                <addr>%s:%s</addr>
                <encoding_profile>%s</encoding_profile>
            </cbr_sources>''' % (str(cbr_multicast_array[j]),str(cbr_port_array[j]),str(cbr_enc_id[j]))
                else:
                    msg10 = '''
            <cbr_sources>
                <addr>%s:%s</addr>
                <encoding_profile>%s</encoding_profile>
                <source_addrs>%s:0</source_addrs>
            </cbr_sources>
            <cbr_live_pause>%s</cbr_live_pause>''' % (str(cbr_multicast_array[j]),str(cbr_port_array[j]),str(cbr_enc_id[j]),str(params.cbr_igmp_source_addr),str(params.pause))                    
                orig_port += 1
                msg9 += msg10
        else:
            mssg9= ''
        msg11= '''
        <specialize_compression_enable>%s</specialize_compression_enable>
    </channel>
</X>''' % (str(params.sc_enable))
        msg = msg1 + msg2 +  msg3 + msg4 + msg6 + msg7 + msg8 + msg9 + msg11
        
        print msg
        msg_len  = len(msg)
        msg_header = '''POST /multicast_channel/update HTTP/1.1
Content-Length: %s
Content-Type: text/x-xml2
Host: %s
Connection: Keep-Alive
User-Agent: Apache-HttpClient/4.2.5 (java 1.5)

''' % (str(msg_len),str(params.manager))

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((manager_ip,int(manager_port) )) 
        s.send(msg_header)
        s.sendall(msg)
        print str(msg)
        datarecv=s.recv(1024)
        print "Reply Received: "+ str(datarecv)
        if (params.is_abr_channel == 1 or params.is_abr_channel == 2):
            if (params.only_one_multicast == 0 ):
                fake_IP_nums = stb_ip_parse(params.multicast_addr)
                #print fake_IP_nums
                if fake_IP_nums[3] > 253:
                    fake_IP_nums[3] = 0
                    fake_IP_nums[2] += 1 
                                    
                #re-assemble the fake ip string           
                fake_IP_nums[3] = int(fake_IP_nums[3])
                fake_IP_nums[3] += 1
                params.multicast_addr = str_stb_ip_parse(fake_IP_nums)
                orig_port = params.start_port
            else:
                orig_port = params.start_port                
        else:
            if (params.only_one_multicast == 0 ):
                if params.one_fake_machine == 1: # sending to incremental fake port
                    params.start_port += 1        
                else : # Sending to incremental IP
                    fake_IP_nums = stb_ip_parse(params.multicast_addr)
                    #print fake_IP_nums
                    if fake_IP_nums[3] > 253:
                        fake_IP_nums[3] = 0
                        fake_IP_nums[2] += 1 
                                        
                    #re-assemble the fake ip string           
                    fake_IP_nums[3] = int(fake_IP_nums[3])
                    fake_IP_nums[3] += 1
                    params.multicast_addr = str_stb_ip_parse(fake_IP_nums)
            else:
                pass

        
        
    
     
def addChannelEncdingProfile():
    global params ,cbr_multicast_array,cbr_port_array
    global channels_name_id_dictionary
    if params.is_abr_channel != 0:
        enc_id = UpdateEncodingProfile()
    cbr_enc_id = UpdateEncodingProfileCBR()
    layers_bw_list = params.layers_bw.split(',')
    orig_port = params.start_port
    manager_ip = params.manager[:string.find(params.manager,":")]
    manager_port = int(params.manager[string.find(params.manager,":") + 1:])
    ad_zone_sufix = 0
    
    pods_array = params.pods_ids.split(';')
    
    objs = "RS"
    pods_percentage_array = map(int, params.pods_dist_to_chnl.split(';'))   
    pods_counter = [0] * len(pods_array)
    
    #freqs = [int(cfg.ff_percent),int(cfg.rew_percent),int(cfg.pause_percent)]        
    wc = wchoice(pods_array, pods_percentage_array, filter=False)
    
    channel_by_pods = [wc() for _ in xrange(params.num_channel_map)]
    
    
    if (params.update_channels == 1):
        channel_name_id()
        
    for i in range (params.num_channel_map):
        if(params.use_edge_ids == 1):
            edge_id=str(channel_by_pods[i%params.num_channel_map])
        else:
            edge_id='0'
        
        if (params.update_channels == 1):
            name = "%s%s" % (str(params.channel_prefix),str(i))
            id = channels_name_id_dictionary[str(name)]
            update=1
        else:
            update=0
            id=0
        msg1 = '''<X>
  <update>%s</update>
  <channel>
  <name>%s%s</name>
  <addr>%s:%s</addr>
  <source_addrs>
  <size>0</size>
  </source_addrs>
  <is_ok>1</is_ok>
  <id>%s</id>
    ''' %  (str(update),str(params.channel_prefix),str(i),str(cbr_multicast_array[0]),str(cbr_port_array[0]),str(id))
        
        if params.ad_zone_identical==0:
            ad_zone_sufix += int(i+1)
        elif  params.ad_zone_identical==1:
            ad_zone_sufix = 1
        elif  params.ad_zone_identical==2:
            ad_zone_sufix = str('')
        msg2 = '''<ad_zone>%s%s</ad_zone>
    ''' % (str(params.ad_zone_prefix),str(ad_zone_sufix))
        if params.ad_zone_identical== -1:
            msg2 = '''<ad_zone></ad_zone>
    '''
        bw_layers_for_channel = layers_bw_list[int(i%len(layers_bw_list))]
        if(params.is_abr_channel == 1 or params.is_abr_channel == 2):
            msg3 = '''<active>1</active>
    <monitor>%s</monitor>
    <encoding_profile>%s</encoding_profile>
    <abr>
      <live>1</live>
      <source_addr>0.0.0.0:0</source_addr>
      <vbr>1</vbr>
        <edge_id>%s</edge_id>
      <layers>
        <size>%s</size>
        ''' % (str(params.monitor),str(cbr_enc_id[0]),str(edge_id),str(len(layers_bw_list)))
        else:
            msg3 = '''<active>1</active>
    <monitor>%s</monitor>
    <encoding_profile>%s</encoding_profile>
    <abr>
      <live>0</live>
      <source_addr>0.0.0.0:0</source_addr>
      <vbr>0</vbr>
      <layers>
        <size>0</size>
        ''' % (str(params.monitor),str(cbr_enc_id[0]))
            
               
        msg5 = ''
        if(params.is_abr_channel == 1 or params.is_abr_channel == 2):
            for j in range(len(layers_bw_list)):
                msg4 = '''        <elem id="%s">
          <live_feed_address>%s:%s</live_feed_address>
          <status>1</status>
          <encoding_profile>%s</encoding_profile>
        </elem>
        ''' % (str(j),str(params.multicast_addr),str(orig_port),str(enc_id[j]))
                orig_port += 1
                msg5 += msg4
        if params.cbr_live == 0:
            msg6 = '''      </layers>
    </abr>
    <live>1</live>
    <cbr_live>0</cbr_live>
        <cbr_edge_id>%s</cbr_edge_id>
        <specialize_compression_enable>%s</specialize_compression_enable>
  </channel>
</X>''' % (str(edge_id),str(params.sc_enable))
        else:
            msg6 = '''      </layers>
    </abr>
    <live>1</live>
    <cbr_live>1</cbr_live>
    <specialize_compression_enable>%s</specialize_compression_enable>
  </channel>
</X>''' % (str(params.sc_enable))         
  
        msg =  msg1 + msg2 + msg3 + msg5 + msg6
        print msg
        msg_len  = len(msg)
        msg_header = '''POST /multicast_channel/update HTTP/1.1
User-Agent: Jakarta Commons-HttpClient/3.1
Host: %s
Content-Length: %s
Content-Type: text/xml; charset=utf-8

''' % (str(params.manager),str(msg_len))

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((manager_ip,int(manager_port) )) 
        s.send(msg_header)
        s.sendall(msg)
        print (msg_header) + str(msg)
        datarecv=s.recv(1024)
        print "Reply Received: "+ str(datarecv)
        if (params.is_abr_channel == 1 or params.is_abr_channel == 2):
            if (params.only_one_multicast == 0 ):
                fake_IP_nums = stb_ip_parse(params.multicast_addr)
                #print fake_IP_nums
                if fake_IP_nums[3] > 253:
                    fake_IP_nums[3] = 0
                    fake_IP_nums[2] += 1 
                                    
                #re-assemble the fake ip string           
                fake_IP_nums[3] = int(fake_IP_nums[3])
                fake_IP_nums[3] += 1
                params.multicast_addr = str_stb_ip_parse(fake_IP_nums)
                orig_port = params.start_port
            else:
                orig_port = params.start_port                
        else:
            if (params.only_one_multicast == 0 ):
                if params.one_fake_machine == 1: # sending to incremental fake port
                    params.start_port += 1        
                else : # Sending to incremental IP
                    fake_IP_nums = stb_ip_parse(params.multicast_addr)
                    #print fake_IP_nums
                    if fake_IP_nums[3] > 253:
                        fake_IP_nums[3] = 0
                        fake_IP_nums[2] += 1 
                                        
                    #re-assemble the fake ip string           
                    fake_IP_nums[3] = int(fake_IP_nums[3])
                    fake_IP_nums[3] += 1
                    params.multicast_addr = str_stb_ip_parse(fake_IP_nums)
            else:
                pass
    

def CheckMultiCastIp(ip):
    print "the MC IP: ", ip 
    theIP = stb_ip_parse(ip)
    if my_is_int(theIP[0]) != True :
        return 0
    elif (int(theIP[0]) > 238):
        return 0
    elif (int(theIP[0]) < 224):
        return 0
    elif my_is_int(theIP[1]) != True :
        return 0
    elif (int(theIP[1]) < 0):
        return 0
    elif (int(theIP[1]) > 255):
        return 0 
    elif my_is_int(theIP[2]) != True :
        return 0
    elif (int(theIP[2]) < 0):
       return 0
    elif (int(theIP[2]) > 255):    
       return 0 
    elif my_is_int(theIP[3]) != True :
        return 0
    elif (int(theIP[3]) < 0):
       return 0
    elif (int(theIP[3]) > 255):    
       return 0
    else:
       return 1


def CreateChannelFile(file, path):
    global channels
    try:
            channels_file = open(path+"/" +file, "w")
            
    except IOError:
            print "Channels file can not be found.\nScript finished."
            sys.exit(0)
    channel_len = int (len(channels))
    for i in range (channel_len) :
         if (i+1) < channel_len:
            channels_file.write("%s%s" % (channels[i],"\n"))
         else:
            channels_file.write("%s" % (channels[i]))
    channels_file.close()
    
  
def get_manager_version(manager):
    manager_parse_ver = None
    try:
        try :
            manager_ver_url = "http://%s/get_versions?X=0" % (manager)
            #print manager_ver_url
            manager_ver_open_url=urllib2.urlopen(manager_ver_url)
            manager_ver_response = manager_ver_open_url.read()
            manager_parse_ver = libxml2.parseDoc(manager_ver_response)
            manager_ver = addByxPath(manager_parse_ver, "//X/mngr_ver")
            #CM_ver = addByxPath(manager_parse_ver, "//X/cm_ver")
            #print "manager version --> " + str(manager_ver)
            
        except :
            print("=!=!=!=!=!=!=!=!=!=!=!=!=!=!" + "\n" + "Manager didn't respond ...\n" + "Script exit\n" + "=!=!=!=!=!=!=!=!=!=!=!=!=!=!")  
            sys.exit()
        
    finally:
        if manager_parse_ver:
            manager_parse_ver.freeDoc()
        
    return manager_ver  
 

# Editing the XML for the Streamer load
def addByxPath(dom, xpath):               
    list = dom.xpathEval(xpath)
    for url in list:
        o = url.content
        #print "o in function-->" +params.manager o
    return o
  
def stb_ip_parse(ip):
    
        ipNums = ip.split('.')
        ipNums[0] = int(ipNums[0]) 
        ipNums[1] = int(ipNums[1])
        ipNums[2] = int(ipNums[2])
        ipNums[3] = int(ipNums[3])
        
        return ipNums    
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def main():
       
    global params,enc_array,cbr_multicast_array,cbr_port_array
    global channels
    global channels_to_del
    global channels_to_del_is_abr
    global channels_to_del_is_cbr
    global channels_name_id_dictionary
    channels_to_del = []
    channels_to_del_is_abr = []
    channels_to_del_is_cbr = []
    channels_name_id_dictionary = {}
    #path = os.getcwd()
    path = "../"
    channel_file = "channels.list"
    
    
    if params.delete_channels == 'n':
        if (params.is_abr_channel == 0):
            channels = ConChannelMap(version_num)
            if ((version_num[0] == 2) and (version_num[1] == 6) and (version_num[3] >= 4)) or ((version_num[0] == 2) and (version_num[1] <= 8) and (version_num[3] < 4)):            
                CreateChannelFile(channel_file, path)            
            else:                
              addChannelEncdingProfile()  
        elif params.is_abr_channel == 1 or params.is_abr_channel == 2:           
            #channels = ConAbrChannelMap(version_num) 
            #addChannelEncdingProfile()
            addChannelEncdingProfileXML5()
        elif params.is_abr_channel == 3:
            addChannelCbrSeveralMulticast()
    else:
         get_all_channels()
if __name__ == "__main__":
    
    
    # Getting current folder location
    #path = os.getcwd()
    path = "../"
    # Reading Configuration file
    config = ConfigObj(path + "conf/config.ini")
    params = globalParams()
    pars_INI_file(config)
    enc_array=params.cbr_layer_type_for_cvc.split(",")
    cbr_multicast_array=params.multicast_for_cbr.split(",")
    cbr_port_array=params.multicast_start_port_for_cbr.split(",")
    manager_version = get_manager_version(params.manager)
    version_num = stb_ip_parse(manager_version)
    
    main()

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


