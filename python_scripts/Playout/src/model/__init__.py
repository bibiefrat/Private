from definitions import Globals
from definitions.DefObjects import PlayoutModeEnum




from model.ABR.AbrSessionManager import AbrSessionManager

from model.LSCP.LscpSessionManager import LscpSessionManager
from model.RTSP.RollingBufferSessionManager import RollingBufferSessionManager

from model.RTSP.RtspSessionManager import RtspSessionManager

_MAX_IP = 0xffffffff

def ip2long(ip):
    """
    Convert a IPv4 address into a 32-bit integer.

    @param ip: quad-dotted IPv4 address
    @type ip: str
    @return: network byte order 32-bit integer
    @rtype: int
    """
    ip_array = ip.split('.')
    ip_long = int(ip_array[0]) * 16777216 + int(ip_array[1]) * 65536 + int(ip_array[2]) * 256 + int(ip_array[3])
    return ip_long
def long2ip (l):
    """
    Convert a network byte order 32-bit integer to a dotted quad ip address.


    >>> long2ip(2130706433)
    '127.0.0.1'

    >>> long2ip(None)
    Traceback (most recent call last):
        ...
    TypeError: unsupported operand type(s) for >>: 'NoneType' and 'int'


    Args:
        l: Network byte order 32-bit integer
    Returns:
        Dotted-quad ip address (eg. '127.0.0.1')
    """
    if _MAX_IP < l < 0:
        raise TypeError, "expected int between 0 and %d inclusive" % _MAX_IP
    return '%d.%d.%d.%d' % (l>>24 & 255, l>>16 & 255, l>>8 & 255, l & 255)


class ipAddr_iter(object):
    def __init__(self,init_ip,init_port,inc_port = False):
        self.init_ip = init_ip
        self.init_port = init_port
        self.inc_port = inc_port
        self.long_ip = ip2long(init_ip)

    def get_next(self):
        if(self.inc_port):
            self.init_port+=1
            return (self.init_ip + ":" +str(self.init_port))
        else:
            self.long_ip +=1
            return (long2ip(self.long_ip) +":" +str(self.init_port))

class ipAddr_distrib(object):
    def __init__(self,num_of_real,real_ip_iter,fake_ip_iter):
        self.num_of_real = num_of_real
        self.real_ip_iter = real_ip_iter
        self.fake_ip_iter = fake_ip_iter
    def get_next(self):
        try:
            if(self.num_of_real>0):
                return self.real_ip_iter.next()
            else:
                raise StopIteration
        except :
            return self.fake_ip_iter.next().get_next()



def SessionManager(networkService,sendingThread):
    if(Globals.cfg.playout_mode == PlayoutModeEnum.RTSP or Globals.cfg.playout_mode == PlayoutModeEnum.NGOD ):
        return RtspSessionManager(networkService,sendingThread)
    elif(Globals.cfg.playout_mode == PlayoutModeEnum.ROLLINGBUFFER) :
        return RollingBufferSessionManager(networkService,sendingThread)
    elif (Globals.cfg.playout_mode == PlayoutModeEnum.LSCP):
        return LscpSessionManager(networkService,sendingThread)
    elif (Globals.cfg.playout_mode == PlayoutModeEnum.HTTP or Globals.cfg.playout_mode == PlayoutModeEnum.ABR_STATIC or Globals.cfg.playout_mode == PlayoutModeEnum.HLS or Globals.cfg.playout_mode == PlayoutModeEnum.ABR_DYNAMIC):
        return AbrSessionManager(networkService,sendingThread)
