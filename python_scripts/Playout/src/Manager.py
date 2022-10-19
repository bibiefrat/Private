
import libxml2
import logging
import socket
import string
import urllib
import urllib2
import time
from definitions import SessExceptions
from definitions.DefObjects import PlayoutModeEnum

import sys
from definitions.DateUtil import strptime
from definitions.Logger import  my_simple_logging_decorator


class Manager(object):
    def __init__(self, manager_ip_port, isSSL, cfg):
        self.manager_ip_port = manager_ip_port

        self.manager_ip = str(manager_ip_port).split(":")[0]
        self.cached = 1
        self.Region_ID = -1
        self.assets_bitrate = {}
        self.log = logging.getLogger(type(self).__name__  + " "+ self.manager_ip )

        self.isSSL = isSSL
        #self.manager_ver, self.CM_ver = self.get_manager_cm_version()
        self.cfg = cfg


    def manager_version(self):
        #print "manager version-->" + str(manager_ver)
        if self.manager_ver == '2.0.0.1':
            return "2.0.0.1"
        elif string.find(self.manager_ver, "2.") != -1:
            return self.manager_ver
        elif string.find(self.manager_ver, "3.") != -1:
            return self.manager_ver
        else:
            return "old"

    def getHTTP(self):
        if self.isSSL:
            return "https://"
        else:
            return "http://"

    def list_checkByxPath(self,dom, xpath):
        elem_list = dom.xpathEval(xpath)
        count=0
        if(len(elem_list)>1):
            r=[]
            for url in elem_list:
                r.append(url.content)
                count+=1
        else:
            r=None
            for url in elem_list:
                r=url.content

        return (count,r)

    def get_xml_dox_from_url(self,url):
        result = urllib2.urlopen(url)
        xml_txt = result.read()
        return libxml2.parseDoc(xml_txt)

    def __get_identity(self):
        #http://server:5929/identity?X=0
        serverUrl = "http://%s/identity?X=0" % (self.manager_ip_port)
        identity_doc = self.get_xml_dox_from_url(serverUrl)
        return self.checkByxPath(identity_doc, "//X/name")

    def DiscoverTopology(self):
        ident =  self.__get_identity()
        streamers = []
        print ident
        if(str(ident).find("Manager") >0 ):

            Region_ID_url = "http://%s/get_topology?X=0" % (self.manager_ip_port)
            Region_doc = self.get_xml_dox_from_url(Region_ID_url)
            Region_ID = self.checkByxPath(Region_doc, "/X/online/regions/elem/id")
            print Region_ID

            topology_url = "http://%s/command/monitor_service?token=&agent=&id=TOPOLOGY&opaque=%s+DATA" % (self.manager_ip_port,Region_ID)
            topology_result = self.get_xml_dox_from_url(topology_url)
            Streamer_ID = self.list_checkByxPath(topology_result, "//X/config/edges/elem/streamers/elem/addr")

            if(Streamer_ID[0] ==0):
                streamers.append(Streamer_ID[1])
            else:
                for streamer in Streamer_ID[1]:
                    streamers.append(streamer)

            return streamers
#
#        else:
#            streamers.append(serverIp)


    def get_manager_cm_version(self):
        manager_ver_url = "%s%s/get_versions?X=0" % (self.getHTTP(), self.manager_ip_port)
        #print manager_ver_url
        manager_ver_open_url = urllib2.urlopen(manager_ver_url)
        manager_ver_response = manager_ver_open_url.read()
        manager_parse_ver = libxml2.parseDoc(manager_ver_response)
        mngr_ver,cm_ver = self.checkByxPath(manager_parse_ver, "//X/mngr_ver"), self.checkByxPath(manager_parse_ver, "//X/cm_ver")
        self.log.debug("Manager version: " + mngr_ver + " cm version: " + cm_ver)
        return mngr_ver, cm_ver

    def get_streamer(self, streamer_id):
        topology_url = "http://%s/command/monitor_service?token=&agent=&id=TOPOLOGY&opaque=%s+DATA" % (
        self.manager_ip_port, self.GetRegion())
        topology_result = urllib2.urlopen(topology_url)
        xml_topology = topology_result.read()
        parse_topology = libxml2.parseDoc(xml_topology)
        #print parse_topology
        streamerVideoIP_node = parse_topology.xpathEval("//X/config/edges/elem/streamers/elem[id='" + streamer_id + "']/video_address")[0]
        streamer = streamerVideoIP_node.content.split(":")[0]
        parse_topology.freeDoc()
        self.log.debug("streamer " + streamer_id + " is " + streamer)
        return streamer

    def get_asset_properties(self, asset_id):
        url = "http://%s/get_asset_properties?external_id=%s&internal_id=0" % (
            self.manager_ip_port, urllib.quote_plus(asset_id))
        all_asset_info = urllib2.urlopen(url)
        xml = all_asset_info.read()
        return xml

    def get_asset_bitrate(self, asset_id):
        if(self.cached == 1):
            if(asset_id in self.assets_bitrate):
                return self.assets_bitrate[asset_id]

        xml = self.get_asset_properties(asset_id)
        all_asset_list = libxml2.parseDoc(xml)
        asset_bitrate_list = all_asset_list.xpathEval("/X/bandwidth")
        for url in asset_bitrate_list:
            asset_bitrate = url.content
        all_asset_list.freeDoc()

        if(self.cached == 1):
            self.assets_bitrate[asset_id] = asset_bitrate
        return asset_bitrate

    @my_simple_logging_decorator
    def get_rolling_buffers(self):
#        try:
        bitrate_type=""
        asset_id_strip = "LIVE$"
        if(self.cfg.playout_mode == PlayoutModeEnum.ABR_DYNAMIC or self.cfg.playout_mode == PlayoutModeEnum.ABR_STATIC):
            bitrate_type = "ABR"

        elif(self.cfg.playout_mode == PlayoutModeEnum.ROLLINGBUFFER):
            bitrate_type = "CBR"
            asset_id_strip = "LIVE_CBR$"


        url = "http://%s/get_all_rolling_buffers?X=0" % (self.manager_ip_port)

        all_rolling_buffers = urllib2.urlopen(url)
        xml = all_rolling_buffers.read()
        all_rolling_buffers_list = libxml2.parseDoc(xml)
        channels = all_rolling_buffers_list.xpathEval("/X/buffers/elem/name")
        channel_map = {}
#        all_rolling_buffers_list.freeDoc()
        for channel in channels :
            if((channel.content in eval(self.cfg.channels) or len(eval(self.cfg.channels))==0 )and (not channel.content in channel_map.keys())):

                self.log.devel("getting content cor channel " +channel.content)
                channel_buffer_url = "http://%s:9090/mixed_status_rolling_buffer/%s/%s/2040-01-01T00:00:00" % (self.manager_ip,channel.content.replace(asset_id_strip,""),self.cfg.slice_start)
    
                channel_buffer = urllib2.urlopen(channel_buffer_url)
                channel_buffer_doc = libxml2.parseDoc(channel_buffer.read())
                #/rolling_buffer_status/channel[@bitrate_type = "ABR"]/inner_buffer[@playable][not(@no_data)]/
                playable_start = channel_buffer_doc.xpathEval("/rolling_buffer_status/channel[@bitrate_type = \""+bitrate_type+"\"]/inner_buffer[@playable][not(@no_data)]/@start_time")
                playable_end =  channel_buffer_doc.xpathEval("/rolling_buffer_status/channel[@bitrate_type = \""+bitrate_type+"\"]/inner_buffer[@playable][not(@no_data)]/@end_time")
                if(len(playable_start)>0 and len(playable_end)>0):
                    channel_map[channel.content] = []
                else:
                    self.log.devel("no " +bitrate_type+ " content in " + channel.content)
                    continue
#                self.log.devel("playable starts " + str(playable_start))
#                self.log.devel("playable ends " + str(playable_end))

                playable_ranges = zip(playable_start,playable_end)
                for start,end in playable_ranges:
    
                    start_seconds = time.mktime(strptime(start.content,"%Y-%m-%dT%H:%M:%SZ").timetuple())
                    end_seconds = time.mktime(strptime(end.content,"%Y-%m-%dT%H:%M:%SZ").timetuple())
                    channel_map[channel.content].append((start_seconds,end_seconds))


        all_rolling_buffers_list.freeDoc()

        return channel_map




    def get_asset_duration(self,asset_id):
        xml = self.get_asset_properties(asset_id)
        all_asset_list = libxml2.parseDoc(xml)
        asset_duration_list = all_asset_list.xpathEval("//X/act_duration")
        for url in asset_duration_list:
            asset_duration = url.content
        all_asset_list.freeDoc()
        return asset_duration

    def manager_pars_response(self, response, xpath):
        #print "xpath-->%s" % (xpath)
        ans = response.xpathEval(xpath)
        #print ans[0].content
        return ans[0].content

    def check_manager_state(self):
        # setting default timeout for manager session
        socket.setdefaulttimeout(60)

        urlManager = "http://%s/identity?X=0" % (self.manager_ip_port)

        #print "url for testing manager = " + str(urlManager)
        try:
            manager_response = urllib2.urlopen(urlManager)
        except urllib2.URLError, err:
            raise SessExceptions.Manager_Err(err.reason, urlManager)

        xml_manager = manager_response.read()
        parse_manager = libxml2.parseDoc(xml_manager)
        manager_ans = self.manager_pars_response(parse_manager, "/X/name")
        ans_length = int(len(manager_ans))
        if (ans_length < 1):
            sys.exit(0)

    def GetRegion(self):
        if(self.cached == 1 and self.Region_ID != -1):
            return self.Region_ID

        Region_ID_url = "http://%s/get_topology?X=0" % (self.manager_ip_port)
        Region_result = urllib2.urlopen(Region_ID_url)
        xml_Region = Region_result.read()
        parse_region = libxml2.parseDoc(xml_Region)
        Region_ID = self.checkByxPath(parse_region, "//X/online/regions/elem/id")
        parse_region.freeDoc()
        if(self.cached == 1):
            self.Region_ID = Region_ID
        return Region_ID

    def checkByxPath(self, dom, xpath):
        list = dom.xpathEval(xpath)
        for url in list:
            r = url.content

        return r

    def get_manager_version(self):
        manager_parse_ver = None
        try:
            try:
                manager_ver_url = "http://%s/get_versions?X=0" % (self.manager_ip_port)
                #print manager_ver_url
                manager_ver_open_url = urllib2.urlopen(manager_ver_url)
                manager_ver_response = manager_ver_open_url.read()
                manager_parse_ver = libxml2.parseDoc(manager_ver_response)

                manager_ver = manager_parse_ver.xpathEval("//X/mngr_ver")[0].content


            except Exception, e:
                self.log.critical(
                    "=!" * 30 + "\n" + " " * 43 + "Manager didn't respond ...\n" + " " * 43 + "Script exit\n" + " " * 43 + "=!" * 30)
                sys.exit()
        finally:
            if manager_parse_ver:
                manager_parse_ver.freeDoc()

        return manager_ver

    def translate_session_id(self, session_id, tostring):
        url = "http://%s/translate_session_id?to_string=%d&id=%s" % (
            str(self.manager_ip_port), tostring, str(session_id))
        session_fx_id = urllib2.urlopen(url)
        xml_fx_id = session_fx_id.read()
        parse_fx_id = libxml2.parseDoc(xml_fx_id)
        fx_id = self.checkByxPath(parse_fx_id, "//X")
        parse_fx_id.freeDoc()
        return fx_id

    def session_playout_state(self, str_session_id, npt=False):
        session_state_url = "http://%s/session_playout_state?type=1&fx_id=%s" % (
        str(self.manager_ip_port), str_session_id)
        session_result = urllib2.urlopen(session_state_url)
        xml_session = session_result.read()
        #print xml_session
        parse_session = libxml2.parseDoc(xml_session)
        if(npt):
            session_state = self.checkByxPath(parse_session, "//X/npt"), self.checkByxPath(parse_session, "//X/end_npt")
        else:
            session_state = self.checkByxPath(parse_session, "//X/session_state")
        parse_session.freeDoc()
        return session_state

    def mng_set_stb_ip(self, streamerIP, session_number, stb_addr):

        url = "%s%s/mng_set_stb_ip?type=1&fx_id=%s&stb_addr=%s" % (
        self.getHTTP(), self.manager_ip_port, session_number, urllib.quote_plus(stb_addr))


        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError, err:
            self.log.error("Error while setting stb ip in streamer.")
            self.log.error(err)
        except Exception, err:
            self.log.error(err)
            raise "Error while setting stb ip in streamer."

        # Checking if the allocate session to the stb has succedded
        mng_stb_url = response.read()

        res_mng_stb = libxml2.parseDoc(mng_stb_url)

        success_mng_stb = self.checkByxPath(res_mng_stb, "//X/success")
        if success_mng_stb == '0':
            err_msg = self.checkByxPath(res_mng_stb, "/X/error")

            self.log.error("Can't assign STB address : %s" , err_msg)
            res_mng_stb.freeDoc()
            return False
        else:
            res_mng_stb.freeDoc()
            return True


    def get_current_session_npt(self, session_id):
        return self.session_playout_state(session_id, True)

    def __str__(self):
        return self.manager_ip_port

    def __repr__(self):
        return self.manager_ip_port