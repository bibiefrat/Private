# File Name: Parser.py
#from email.parser import HeaderParser
import re
import socket
import struct
from datetime import datetime
import urlparse
import itertools
from definitions import DefObjects, SessExceptions, color

import ConfigParser
import libxml2
import logging
import string
import sys
import urllib2
import urllib

class atdict(dict):
    __getattr__= dict.__getitem__
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

cfg_defaults=eval(open("definitions/cfg_defaults").read().replace("\r\n", ""))
#    {'trickplay_list_path': 'conf/trickplay.lscp',
#              'sessions_per_second': "1",
#              'fake_stb': '20.0.0.90',
#              'channels': '["abr_cbr"]',
#              'manager': '192.168.6.50:5929',
#              'sleep_after_play': '0.01',
#              'single_connection': "0",
#              'start_sessions_after_allocation': "1",
#              'hls_device_profile': 'HLS',
#              'lscp_status': "1",
#              'sessions_change_level_percent': "0",
#              'manifest_only': "0",
#              'service_group': '00000000000D',
#              'manager_ip': '192.168.6.50',
#              'warning_inner_assets': "0",
#              'start_at_random_level': "2",
#              'streamer_ip': '192.168.5.65:5555',
#              'init_port': "1211",
#              'no_delay_sessions': "200",
#              'slice_duration': '00:05:00',
#              'start_npt': "0",
#              'stat_delay': "1",
#              'pause_percent': "0",
#              'streamer_id': "0",
#              'loop_mode': "0",
#              'sys_exit_on_critical': "0",
#              'smooth_device_profile': 'SMOOTH',
#              'slice_buffer': "1",
#              'total_sessions': "1",
#              'real_session': "0",
#              'trick_play_percent': "0",
#              'abr_session_type': "2",
#              'enable_ssl': "0",
#              'desired_log_level': 'Devel',
#              'buffer_sampling_interval': "1",
#              'slow_motion': "0",
#              'fragment_length': "5",
#              'real_stb': '192.168.7.105:1234',
#              'lsc_tool_play_resume': 'R',
#              'rew_percent': "0",
#              'ff_percent': "100",
#              'run_duration': "300000",
#              'tear_down_per_sec': "0",
#              'command_duration': "120",
#              'is_numeic_session_id': "0",
#              'playout_mode': "7",
#              'number_of_sending_threads': "10",
#              'one_fake_machine': "1",
#              'asset_list_path': 'conf/AbrList.txt',
#              'geo_id': "6",
#              'rtsp_close_socket_once': "1",
#              'print_alloc_time': "0",
#              'create_asset_list': "1",
#              'delay_between_sessions': "1",
#              'log_file': 'log/log.txt',
#              'lscp_command_timeout': "3",
#              'lsc_protocol': "1"}

class Parser:
    def __init__(self):
        self.color_loc = color.TerminalController()
        self.log = logging.getLogger("Parser")
        self.INI = ""
        pass

    def get_assets(self, file, Manager, path,rollingBuffer):
        try:
            asset_file = open(file , "r")
        except IOError:
            print self.color_loc.render('${RED}Asset file can not be found.\nScript finished.${NORMAL}')
            sys.exit(0)

        all_lines = asset_file.readlines()
        num_asset_lines = len(all_lines)
        #print num_asset_lines
        failed_parsing_asset = 0
        assets = []

        for single_lines in all_lines:
            session_assets = []
            #inner_assets = str(single_lines).split(":")
            inner_assets = str(single_lines).split(";")
            try:
                for line_asset in inner_assets:
                    innerData = line_asset.split()
                    if innerData[2].strip() == "-1":
                        parse_dur_res = None
                        print "asset details - name = %s, start = %s, end = %s" % (
                        innerData[0], innerData[1], innerData[2])
                        # Calculating each asset duration
                        duration_url = "http://%s/get_asset_properties?external_id=%s&internal_id=0" % (
                        Manager, urllib.quote_plus(innerData[0]))
                        # Duration calculation for old versions
                        #duration_url = "http://%s/get_asset_properties?X=%s" % (Manager, innerData[0])

                        try:
                            duration_response = urllib2.urlopen(duration_url)
                        except urllib2.URLError, err:
                            raise SessExceptions.SessAllocate_Err(0, err.reason, duration_url)

                        xml_dur_res = duration_response.read()

                        try:
                            if xml_dur_res.find("?xml") > 0:
                                parse_dur_res = libxml2.parseDoc(xml_dur_res)
                            else:
                                failed_parsing_asset += 1
                                raise SessExceptions.xml_parse_err(innerData[0], duration_url, xml_dur_res)

                        except libxml2.parserError:
                            if parse_dur_res:
                                parse_dur_res.freeDoc()
                            failed_parsing_asset += 1
                            raise SessExceptions.xml_parse_err(innerData[0], duration_url, xml_dur_res)

                        asset_duration = float(
                            int(self.parse_response(parse_dur_res, "//X/act_duration")) - int(innerData[1]))
                        parse_dur_res.freeDoc()
                        #print "asset duration --> " + str(asset_duration)

                    else:
                        if(not rollingBuffer):
                            asset_duration = float(int(innerData[2]) - int(innerData[1]))
                        else:
                            if(innerData[1] == "LIVE" or innerData[2] == "END"):
                                asset_duration = 2000000
                            else:
                                start = datetime.strptime(innerData[1], "%Y-%m-%dT%H:%M:%S")
                                end =  datetime.strptime(innerData[2], "%Y-%m-%dT%H:%M:%S")
                                duration =    end-start
                                asset_duration =  duration.seconds

                        #print "asset_duration' is not defined

                    asset = DefObjects.Asset(innerData[0], innerData[1], innerData[2].rstrip(), asset_duration)
                    #print "asset = " + str(innerData[0]) + str(innerData[1]) + str(innerData[2]) + str(asset_duration)
                    session_assets.append(asset)

            except SessExceptions.xml_parse_err, err:
                self.log.error(err)
                if failed_parsing_asset < num_asset_lines:
                    continue
                else:
                    print self.color_loc.render('${RED}All assets are invalid.\nScript finished.${NORMAL}')
                    sys.exit(0)

            assets.append(session_assets)

        return assets

    # Parsing session allocate response for RTSP and Session ID
    def url_sess_response(self, r):
        rtsp_session = r[string.find(r, "rtsp"):string.rfind(r, "\">")]
        session_string = rtsp_session[string.rfind(rtsp_session, "/") + 1:]
        streamer = rtsp_session[string.rfind(rtsp_session, "://") + 3:string.rfind(rtsp_session, ":")]
        return [session_string, rtsp_session, streamer]



    def parse_response(self, response, xpath):
        list = response.xpathEval(xpath)
        for url in list:
            r = url.content
            #print "r in func =" + r
        return r

    def parse_response_as_array(self, response, xpath):
        list = response.xpathEval(xpath)
        return list


    def ini_parse(self):
        path = "../"
        print "reading configuration file"
        def ConfigSectionMap(section):
            dict1 = atdict(cfg_defaults)
            try:

                options = atdict(config.items(section))
#                for k,v in cfg_defaults:
#                    options.setdefault(k,v)

                for k,v in options.items():

                    if(v.isdigit()):
                        options[k] = int(v)

            except ConfigParser.NoSectionError:
                print self.color_loc.render('${RED}Configuration file can not be found.\nScript finished.${NORMAL}')
                sys.exit(0)
#            for option in options:
#                try:
#                    dict1[option] = config.get(section, option)
#                    if dict1[option] == -1:
#                        DebugPrint("skip: %s" % option)
#                except:
#                    print("exception on %s!" % option)
#                    dict1[option] = None
            return options


        ini = DefObjects.INI()

        config = ConfigParser.ConfigParser(cfg_defaults)

        cfgPath = "%s%s" % (path, "/conf/config.ini")
        config.read(cfgPath)

        dict = ConfigSectionMap("Configuration")
        #all_lines = config_file.readlines()

        dict["manager_ip"] = dict["manager"].split(":")[0]
        dict["single_connection"] = False
        #print "Configuration file parameters = " + all_lines
#        ini.asset_list_path = dict['asset_list_path']
#        ini.logfile = dict['log_file']
#        ini.manager = dict['manager']
#        ini.manager_ip = dict['manager'].split(":")[0]
#        ini.real_stb = dict['real_stb']
#        ini.streamer_id = dict['streamer_id']
#        ini.loop_mode = int(dict['loop_mode'])
#        ini.fake_stb = dict['fake_stb']
#        ini.num_real_session = dict['real_session']
#        ini.total_sessions = int(dict['total_sessions'])
#        ini.sec_delay_sessions = float(dict['delay_between_sessions'])
#        ini.no_delay_sessions = int(dict['no_delay_sessions'])
#        ini.tricksFile = dict['trickplay_list_path']
#        ini.log_level = dict['desired_log_level']
#        ini.enable_ssl = int(dict['enable_ssl'])
#        ini.one_fake_machine = int(dict['one_fake_machine'])
#        ini.init_port = int(dict['init_port'])
#        ini.total_duration = dict['run_duration']
#        ini.playout_mode = int(dict['playout_mode'])
#        ini.srvGrp = str(dict['service_group'])
#        ini.act_status = int(dict['lscp_status'])
#        ini.stat_dly = float(dict['stat_delay'])
##        ini.machine_64bit = int(dict['machine_64bit'])
#        ini.print_alloc_time = int(dict['print_alloc_time'])
#        ini.LSC_Transport_Layer = int(dict['lsc_protocol'])
#        ini.slow_motion = int(dict['slow_motion'])
#        ini.tear_down_per_sec = int(dict['tear_down_per_sec'])
#        ini.command_duration = int(dict['command_duration'])
#        ini.trick_play_percent = int(dict['trick_play_percent'])
#        ini.sleep_after_play = float(dict['sleep_after_play'])
#        ini.ff_percent = int(dict['ff_percent'])
#        ini.rew_percent = int(dict['rew_percent'])
#        ini.pause_percent = int(dict['pause_percent'])
#        ini.lsc_tool_play_resume = str(dict['lsc_tool_play_resume'])
#        ini.start_npt = int(dict['start_npt'])
#        ini.rtsp_close_socket_once = int(dict['rtsp_close_socket_once'])
#        ini.create_asset_list = int(dict['create_asset_list'])
#        ini.start_at_random_level = int(dict['start_at_random_level'])
#        ini.sessions_change_level_percent = int(dict['sessions_change_level_percent'])
#        ini.sessions_per_second = int(dict['sessions_per_second'])
#        ini.slice_buffer = int(dict['slice_buffer'])
#        ini.slice_duration = dict['slice_duration']
#        ini.hls_device_profile = dict['hls_device_profile']
#        ini.smooth_device_profile = dict['smooth_device_profile']
#        ini.manifest_only = int(dict['manifest_only'])
#        ini.abr_session_type = int(dict['abr_session_type'])
#        ini.streamer_ip =  str(dict['streamer_ip'])
#        ini.lscp_command_timeout = int(dict['lscp_command_timeout'])
#        ini.geo_id = int(dict['geo_id'])
#        ini.is_numeic_session_id = int(dict['is_numeic_session_id'])
#        ini.start_sessions_after_allocation = int(dict['start_sessions_after_allocation'])
#        ini.buffer_sampling_interval  = int(dict['buffer_sampling_interval'])
#        ini.fragment_length = (dict['fragment_length'])
#        ini.warning_inner_assets =  int(dict['warning_inner_assets'])
#        ini.sys_exit_on_critical =int(dict['sys_exit_on_critical'])
#        ini.number_of_sending_threads =int(dict['number_of_sending_threads'])
        print dict
        self.INI = dict
        return dict

    def lscp_tricks(self, file, path):
        f = file.split(".")

        #print "file: ", file
        #print "path: ", path

        if f[1] != "lscp":
            print self.color_loc.render('${RED}Wrong trick file, Should be lscp.\nScript finished.${NORMAL}')
            sys.exit()

        try:
            tricks_file = open(path + "/" + file, "r")
        except IOError:
            print self.color_loc.render('${RED}Trick file can not be found.\nScript finished.${NORMAL}')
            sys.exit()

        trickLength = 0

        all_lines = tricks_file.readlines()

        play_tricks = []

        for single_lines in all_lines:
            line = str(single_lines).split(" ")
            if line[0] == '#':
                continue

            trick = DefObjects.lscpTricks(line[0], int(line[1]), line[2], line[3], line[4],
                                          line[5].rstrip()) # tricks object - defined in DefObjects.py
            trickLength += int(trick.runTime) # sum of all trickplays duration

            play_tricks.append(trick)

        return (play_tricks, trickLength)


    def parse_trickPlays(self, file, path):
        try:
            tricks_file = open(path + "/" + file, "r")
        except IOError:
            print self.color_loc.render('${RED}Trick file can not be found.\nScript finished.${NORMAL}')
            sys.exit()

        trickLength = 0

        all_lines = tricks_file.readlines()

        play_tricks = []

        for single_lines in all_lines:
            line = str(single_lines).split(" ")

            trick = DefObjects.tricks(line[0], line[1], line[2],
                                      line[3].rstrip()) # tricks object - defined in DefObjects.py
            trickLength += int(trick.runTime) # sum of all trickplays duration

            play_tricks.append(trick)

        return (play_tricks, trickLength)


    def stb_ip_parse(self, ip):
        return map(int,ip.split("."))

    def str_stb_ip_parse(self, ip):
        return ".".join(map(str,ip))

    def dottedQuadToNum(self,ip):
        "convert decimal dotted quad string to long integer"
        return struct.unpack('!L',socket.inet_aton(ip))[0]

    def numToDottedQuad(self,n):
        "convert long int to dotted quad string"
        return socket.inet_ntoa(struct.pack('!L',n))


    def get_code_desc(self, buffer):
        code_desc =re.search(r"RTSP/1.0 (?P<code>.*?)\s(?P<desc>.*?)\r\n",buffer)
        return int(code_desc.group(1)),code_desc.group(2)

    def parse_host_from_url(self,buffer):
        parsed =  urlparse.urlparse(buffer)
        server,port = parsed.netloc.split(":")
        sessionid = parsed.path.replace("/","")
        return urlparse.urlparse(buffer).netloc.split(":")






if __name__ == "__main__":
    mylist = [1,2,3]

    iter1 = itertools.cycle(mylist)

    for i in xrange(3):
        print iter1.next()
    print ""
    mylist.extend([4,5,6])
#    p_iter =itertools.cycle(iter(iter1))
    mylist.append([7,8])

    for i in xrange(6):
        print iter1.next()
    print ""
    #parser = Parser()
    #ip,port = parser.parse_host_from_url("RTSP://192.168.1.1:554/$SESSION_ID")
    #print ip,port
#    cfg = parser.ini_parse()
#    print cfg.asset_path
#    print cfg.logfile
#    print cfg.manager
#    print cfg.real_stb
#    print cfg.fake_stb
#    print cfg.num_real_session
#    print cfg.total_sessions
#    print cfg.num_trick_loop
#    print cfg.sec_delay_sessions
#    print cfg.no_delay_sessions
#    print cfg.endless_loop
#    print cfg.total_duration
#    print cfg.enable_ssl
#    print cfg.one_fake_machine
#    print cfg.tricksFile
#    print cfg.init_port
#    print cfg.machine_64bit
#    print cfg.streamer_id
#    print cfg.loop_mode