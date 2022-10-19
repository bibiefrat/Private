# File Name: DefObjects.py


class Enum(int):

    def __new__(cls, value):
        if isinstance(value, str):
            return getattr(cls, value)
        elif isinstance(value, int):
            return cls.__index[value]

    def __str__(self): return self.__name
    def __repr__(self): return "%s.%s" % (type(self).__name__, self.__name)

    class __metaclass__(type):
        def __new__(mcls, name, bases, attrs):
            attrs['__slots__'] = ['_Enum__name']
            cls = type.__new__(mcls, name, bases, attrs)
            cls._Enum__index = _index = {}
            for base in reversed(bases):
                if hasattr(base, '_Enum__index'):
                    _index.update(base._Enum__index)
                # create all of the instances of the new class
            for attr in attrs.keys():
                value = attrs[attr]
                if isinstance(value, int):
                    evalue = int.__new__(cls, value)
                    evalue._Enum__name = attr
                    _index[value] = evalue
                    setattr(cls, attr, evalue)
            return cls


class errorObj:
    def __init__(self):
        self.time = ""
        self.message = ""
        self.sessNumber = ""
        self.loopNumber = ""
        self.urlSent = ""


class Asset(object):
    def __init__(self, id, start, end, duration):
        self.id = id
        self.start = start
        self.end = end
        self.duration = duration


class lscpTricks:
    def __init__(self, mode, scale, start, end, runTime, wait):
        self.mode = mode
        self.scale = scale
        self.start = start
        self.end = end
        self.runTime = int(runTime)
        self.wait = wait


class tricks:
    def __init__(self, scale, start, end, runTime):
        self.scale = scale
        self.start = start
        self.end = end
        self.runTime = int(runTime)


class INI:
    def __init__(self):
        self.asset_list_path = ""
        self.single_connection = False
        self.logfile = ""
#        self.trickplay_list_path = ""
        self.manager = ""
        self.real_stb = ""
        self.fake_stb = ""
        self.real_session = ""
        self.total_sessions = ""
        self.num_trick_loop = ""
        self.endless_loop = ""
        self.sec_delay_sessions = ""
        self.playout_mode = ""



class PlayoutModeEnum(Enum):
    HTTP = 0
    LSCP = 1
    RTSP = 2 #shaw
    ABR_DYNAMIC = 3
    ABR_STATIC = 4
    HLS = 5
    NGOD = 6
    ROLLINGBUFFER = 7



def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance




if __name__ == "__main__":
    a=[1,2,3]
    b=a
    c = a[:]
    a.append(4)
    print c
