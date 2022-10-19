
from StringIO import StringIO

import httplib
import libxml2

import urllib2
from urlparse import urlparse
import datetime
import time

import itertools
import exceptions
from ConfigReader import cfg
from definitions import Globals
from definitions.DateUtil import strptime
from definitions.DefObjects import Asset, Enum
from definitions.Logger import my_simple_logging_decorator#, timeit
from definitions.TZinfo import LocalTimezone, UTC



Local = LocalTimezone()
Utc = UTC()

class CriticalErr(exceptions.Exception):
    def __init__(self, numSess, reason, url, *args, **kwargs):
        exceptions.Exception.__init__(self, *args, **kwargs)
        self.numSess = numSess
        self.reason = reason
        self.url = url
        return
    def __str__(self, *args, **kwargs):
        return "session " + self.numSess + " \""+ self.reason + "\" as response to " + self.url

class ManagerAllocationErr(CriticalErr):
    def __init__(self, numSess, reason, url, *args, **kwargs):
        CriticalErr.__init__(self, numSess, reason, url, *args, **kwargs)

    #        super(ManagerAllocationErr, self).__init__(numSess, reason, url, *args, **kwargs)



class ManifestParsingErr(CriticalErr):
    def __init__(self, numSess, reason, url, *args, **kwargs):
        CriticalErr.__init__(self, numSess, reason, url, *args, **kwargs)

    #        super(ManifestParsingErr, self).__init__(numSess, reason, url, *args, **kwargs)


class FragmentListParsingErr(CriticalErr):
    def __init__(self, numSess, reason, url, *args, **kwargs):
        CriticalErr.__init__(self, numSess, reason, url, *args, **kwargs)

    #        super(FragmentListParsingErr, self).__init__(numSess, reason, url, *args, **kwargs)

class ZipExhausted(Exception):
    pass

def next(iter):
    return iter.next()

def izip_longest(*args, **kwds):
    # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    fillvalue = kwds.get('fillvalue')
    counter = [len(args) - 1]
    def sentinel():
        if not counter[0]:
            raise ZipExhausted
        counter[0] -= 1
        yield fillvalue
    fillers = itertools.repeat(fillvalue)
    iterators = [itertools.chain(it, sentinel(), fillers) for it in args]
    try:
        while iterators:
            yield tuple(map(next, iterators))
    except ZipExhausted:
        pass

def from_iterable(iterables):
    # chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
    for it in iterables:
        for element in it:
            yield element

@my_simple_logging_decorator
def get_rolling_buffers_as_assets():
    tmp_buff = {}
    buffer_list = Globals.managerObj.get_rolling_buffers()
    lists = []
    for channel_name,buff_list in buffer_list.items():
        if(tmp_buff.has_key(channel_name)):
            new_slices = tmp_buff[channel_name].extend(buff_list)
        else:
            tmp_buff[channel_name] = RollingBufferChannel(channel_name,buff_list)
            new_slices = tmp_buff[channel_name].slices



        assets = [AbrAsset(*x) for x in new_slices]
        lists.append(assets)

    return filter(None,list(from_iterable(izip_longest(*lists))))

class AssetList(list):
    def __init__(self):
        super(AssetList, self).__init__()

    def extend(self, iterable):
#        for i in iterable:
#            if(not i in self):
        super(AssetList, self).extend(iterable)


def get_seconds_from_timedelta(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6


class RollingBufferChannel(object):
    def __init__(self,channel_name,buffer_list):
        hours, minutes, seconds = map(int, cfg.slice_duration.split(":"))
        self.duration = datetime.timedelta(seconds=seconds, hours=hours, minutes=minutes)
        self.end_time = 0
        self.buffer_list = []
        self.slices = []
        self.name = channel_name
        self.assets = []
        for start,end in buffer_list:
            self.buffer_list.append(RollingBuffer(channel_name,start,end))
        for rb in self.buffer_list:
            self.slices.extend(rb.splice(self.duration))


        self.update_end_time()

    def update_end_time(self):
        self.end_time =strptime(self.slices[len(self.slices)-1][2],"%Y-%m-%dT%H:%M:%S") + datetime.timedelta(seconds=10)
        self.end_time = time.mktime(self.end_time.timetuple())

    def extend(self,new_list):
        new_slices = None
        for start, end in new_list:
            if(start>self.end_time or end >self.end_time):
                rb = RollingBuffer(self.name,self.end_time,end)
                self.buffer_list.append(rb)
                new_slices = rb.splice(self.duration)
                self.slices.extend(new_slices)
                self.update_end_time()

        return new_slices




class RollingBuffer(object):
    def __init__(self,name,start,end):
        self.name = name
        self.start_ts = start
        self.end_ts = end
        self.start = datetime.datetime.fromtimestamp(float(start)) +datetime.timedelta(seconds=1)
        self.end = datetime.datetime.fromtimestamp(float(end))

    def splice(self,duration):
        total = self.end - self.start
        diff = datetime.timedelta(seconds=10)
        chunk_list = []
        chunks = get_seconds_from_timedelta(total)/(get_seconds_from_timedelta(duration)+10)
        lat_pos = self.start
        for i in xrange(chunks):
            chunk_list.append((self.name,lat_pos.strftime("%Y-%m-%dT%H:%M:%S"),(lat_pos+duration).strftime("%Y-%m-%dT%H:%M:%S")))
            lat_pos+=duration+diff
        return chunk_list

def local_to_utc(local_date):
    """Make sure that the dst flag is -1 -- this tells mktime to take daylight
    savings into account"""
    secs = time.mktime(local_date.timetuple())
    return datetime.datetime.utcfromtimestamp(secs)



def list_checkByxPath(dom, xpath):
    elem_list = dom.xpathEval(xpath)
#
#    if(len(elem_list)>1):
    r=[]
    for url in elem_list:
        r.append(url.content)
#            count+=1
#    else:
#        r=None
#        for url in elem_list:
#            r=url.content

    return r

def get_xml_dox_from_msg(msg):
    return libxml2.parseDoc(msg)

class Fragment(object):
    def __init__(self,length,level,timestamp,format,profile):
        self.length = length
        self.timestamp = timestamp

        self.level = level
        self.fetched = False
        self.format = format
        self.profile = profile


    def __str__(self):
        if(self.profile == AbrSessionProfile.SMOOTH):
            return self.format % self.timestamp
        elif (self.profile == AbrSessionProfile.HLS):
            return "Level("+self.level+")/Segment("+self.timestamp+").ts"

    def __repr__(self):
        return self.__str__()

    #    def __sizeof__(self):
    #        return super(Fragment, self).__sizeof__()

    def __cmp__(self, other):
        return cmp(int(self.timestamp), int(other.timestamp))


    def __eq__(self, other):
        return self.timestamp == other.timestamp



class Fragments(list):
    def __init__(self, listType):
        super(Fragments, self).__init__()
        self.selected_fragment = 0
        self.listType = listType

    def get_fragment(self):
        try:
            fragment = self[self.selected_fragment]
            fragment.fetched = True
            self.__add__(1)
            return fragment
        except Exception,e:
            return None

    def append(self, p_object):
        if(p_object.profile == AbrSessionProfile.SMOOTH or self.listType == AbrAssetType.CLOASED_BUFFER or self.listType == AbrAssetType.VOD_ASSET):
            super(Fragments, self).append(p_object)
            return

        if(p_object in self):
            return
        smaller = False
        for frag in self:
            if(p_object<frag):
                smaller = True
        if(not smaller):
        #            print str(p_object) + " appended"
            super(Fragments, self).append(p_object)

    def remove(self, value):
    #        print "removing " +str(value)
        return super(Fragments, self).remove(value)

    def __add__(self, other):
        if(self.selected_fragment + other >len(self)):
            self.selected_fragment = len(self)-1
        else:
            self.selected_fragment+=other


    def __iadd__(self, other):
        self.__add__(other)


    def __sub__(self, other):

        if(self.selected_fragment - other <0):
            self.selected_fragment = 0
        else:
            self.selected_fragment-=other


    def __isub__(self, other):
        self.__sub__(other)




class FakeSocket(StringIO):

    # a dummy class to wrap StringIO in order to do http parsing
    def makefile(self, *args, **kw):
        return self


def httpparse(msg):
    socket = FakeSocket(msg.read())
    response = httplib.HTTPResponse(socket)
    response.begin()

    return response





class HttpRequest(urllib2.Request):
    def __init__(self, url):
        urllib2.Request.__init__(self, url)

#    def __str__(self):



def percentage(part, whole):
    return  int(round(float(whole)*float(part)/100.0))

#streamers = []


def parse_url(url):
    #'http://192.168.7.216:5555/http_adaptive_streaming/AKBAAAAAFGMOLPAF.m3u8'
    return urlparse(url)[1:3]


def get_server_as_url(server,port = 5929,secured = False):
    if(secured):
        return "https://" + server +":"+port + "/"
    else:
        return "http://" + server +":"+str(port) + "/"


class AbrSessionStateEnum(Enum):
    INIT = -1
    MANAGER_MANIFEST_REQUEST_SENT = 0
    MANAGER_MANIFEST_REQUEST_RECEIVED = 1
    MANIFEST_REQUEST_SENT = 2
    MANIFEST_REQUEST_RECEIVED = 3
    FRAGMENT_LIST_REQUEST_SENT = 4
    FRAGMENT_LIST_REQUEST_RECEIVED = 5
    FRAGMENT_REQUEST_SENT = 6
    FRAGMENT_REQUEST_RECEIVED = 7
    AUDIO_FRAGMENT_REQUEST_SENT = 8
    AUDIO_FRAGMENT_REQUEST_RECEIVED = 9
    CLOSED = 10


class AbrSessionProfile(Enum):
    HLS = 1
    SMOOTH = 2

class AbrSessionType(Enum):
    DYNAMIC = 1
    STATIC = 2


class AbrAssetType(Enum):
    LIVE = 0
    OPEN_BUFFER = 1
    CLOASED_BUFFER = 2
    VOD_ASSET = 3



class AbrAsset(Asset):
    def __init__(self, id, start, end,format = "%Y-%m-%dT%H:%M:%S"):
        self.format = format
        if(not "LIVE" in start and not "END" in end and not id.startswith("/")):
            asset_start = strptime(start, "%Y-%m-%dT%H:%M:%S")
            asset_end =  strptime(end, "%Y-%m-%dT%H:%M:%S")

#            asset_start = datetime.datetime(*(strptime(start, "%Y-%m-%dT%H:%M:%S")[0:6]))
#            asset_end =  datetime.datetime(*(strptime(end, "%Y-%m-%dT%H:%M:%S")[0:6]))

            delta =    asset_end-asset_start
            asset_duration =  delta.seconds
            Asset.__init__(self, id, asset_start, asset_end, asset_duration)
            self.asset_type = None
            if(asset_end>datetime.datetime.utcnow()):
                self.asset_type  = AbrAssetType.OPEN_BUFFER
            elif (asset_end<datetime.datetime.utcnow()):
                self.asset_type  = AbrAssetType.CLOASED_BUFFER
        else:

            if(id.startswith("/")):
                self.asset_type = AbrAssetType.VOD_ASSET
                duration = Globals.managerObj.get_asset_duration(id[1:])
                #duration = 0
                Asset.__init__(self, id, start, end, int(duration))
            else:
                self.asset_type = AbrAssetType.LIVE
                Asset.__init__(self, id, start, end, 6000)

    def __eq__(self, other):
        return self.id==other.id and self.start == other.start and self.end == other.end
    def __cmp__(self, other):
        return self.id==other.id and self.start == other.start and self.end == other.end
#    def __getattr__(self, item):
#        if(item == ""):
#            pass
#

    def __getattribute__(self, name):
        if(name == "start" or name == "end"):
            if(not isinstance(super(AbrAsset, self).__getattribute__(name),str)):
                return super(AbrAsset, self).__getattribute__(name).strftime(self.format)

        return super(AbrAsset, self).__getattribute__(name)

    def __str__(self):
        return  self.id + "\t\t" + str(self.start) + "\t\t" + str(self.end)


    def __repr__(self):
        return "Channel {" + self.id + "} start:{" + str(self.start) + "} end:{" + str(self.end)  + "} - " + str(self.asset_type)










if __name__ == "__main__":
    itertools.cycle(["p","b"])




