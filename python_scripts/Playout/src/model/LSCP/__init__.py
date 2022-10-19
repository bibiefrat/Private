import struct
#from collections import namedtuple
from operator import itemgetter as _itemgetter
from keyword import iskeyword as _iskeyword
import sys as _sys
from definitions.DefObjects import Enum

def namedtuple(typename, field_names, verbose=False, rename=False):
    """Returns a new subclass of tuple with named fields.

    >>> Point = namedtuple('Point', 'x y')
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields
    Point(x=100, y=22)

    """

    # Parse and validate the field names.  Validation serves two purposes,
    # generating informative error messages and preventing template injection attacks.
    if isinstance(field_names, basestring):
        field_names = field_names.replace(',', ' ').split() # names separated by whitespace and/or commas
    field_names = tuple(map(str, field_names))
    if rename:
        names = list(field_names)
        seen = set()
        for i, name in enumerate(names):
            if (not min(c.isalnum() or c=='_' for c in name) or _iskeyword(name)
                or not name or name[0].isdigit() or name.startswith('_')
                or name in seen):
                names[i] = '_%d' % i
            seen.add(name)
        field_names = tuple(names)
    for name in (typename,) + field_names:
        if not min(c.isalnum() or c=='_' for c in name):
            raise ValueError('Type names and field names can only contain alphanumeric characters and underscores: %r' % name)
        if _iskeyword(name):
            raise ValueError('Type names and field names cannot be a keyword: %r' % name)
        if name[0].isdigit():
            raise ValueError('Type names and field names cannot start with a number: %r' % name)
    seen_names = set()
    for name in field_names:
        if name.startswith('_') and not rename:
            raise ValueError('Field names cannot start with an underscore: %r' % name)
        if name in seen_names:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen_names.add(name)

    # Create and fill-in the class template
    numfields = len(field_names)
    argtxt = repr(field_names).replace("'", "")[1:-1]   # tuple repr without parens or quotes
    reprtxt = ', '.join('%s=%%r' % name for name in field_names)
    template = '''class %(typename)s(tuple):
        '%(typename)s(%(argtxt)s)' \n
        __slots__ = () \n
        _fields = %(field_names)r \n
        def __new__(_cls, %(argtxt)s):
            return _tuple.__new__(_cls, (%(argtxt)s)) \n
        @classmethod
        def _make(cls, iterable, new=tuple.__new__, len=len):
            'Make a new %(typename)s object from a sequence or iterable'
            result = new(cls, iterable)
            if len(result) != %(numfields)d:
                raise TypeError('Expected %(numfields)d arguments, got %%d' %% len(result))
            return result \n
        def __repr__(self):
            return '%(typename)s(%(reprtxt)s)' %% self \n
        def _asdict(self):
            'Return a new dict which maps field names to their values'
            return dict(zip(self._fields, self)) \n
        def _replace(_self, **kwds):
            'Return a new %(typename)s object replacing specified fields with new values'
            result = _self._make(map(kwds.pop, %(field_names)r, _self))
            if kwds:
                raise ValueError('Got unexpected field names: %%r' %% kwds.keys())
            return result \n
        def __getnewargs__(self):
            return tuple(self) \n\n''' % locals()
    for i, name in enumerate(field_names):
        template += '        %s = _property(_itemgetter(%d))\n' % (name, i)
    if verbose:
        print template

    # Execute the template string in a temporary namespace
    namespace = dict(_itemgetter=_itemgetter, __name__='namedtuple_%s' % typename,
        _property=property, _tuple=tuple)
    try:
        exec template in namespace
    except SyntaxError, e:
        raise SyntaxError(str(e) + ':\n' + template)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try:
        result.__module__ = _sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return result

class LSCP_status_enum:

    LSCP_OK 			= 0x0       # /* Success*/
    LSCP_BAD_REQUEST    = 0x10      # /* Invalid request*/
    LSCP_BAD_STREAM     = 0x11      # /* Invalid Stream handle*/
    LSCP_WRONG_STATE    = 0x12      # /* Wrong State*/
    LSCP_UNKNOWN        = 0x13      # /* Unknown Error*/
    LSCP_NO_PERMISSION  = 0x14      # /* Client does not have permission for request*/
    LSCP_BAD_PARAM 	    = 0x15      # /* Invalid parameter*/
    LSCP_NO_IMPLEMENT   = 0x16      # /* Not implemented*/
    LSCP_NO_MEMORY      = 0x17      # /* Dynamic memory allocation failure*/
    LSCP_IMP_LIMIT      = 0x18      # /* Implementation Limit exceeded*/
    LSCP_TRANSIENT      = 0x19      # /* Transient Error - reissue*/
    LSCP_NO_RESOURCES   = 0x1a      # /* No resources*/
    LSCP_SERVER_ERROR   = 0x20      # /* Server error*/
    LSCP_SERVER_FAILURE = 0x21      # /* Server has failed*/
    LSCP_BAD_SCALE      = 0x30      # /* Incorrect Scale Value*/
    LSCP_BAD_START      = 0x31      # /* Stream Start time does not exist*/
    LSCP_BAD_STOP       = 0x32      # /* Stream Stop time does not exist*/
    LSCP_MPEG_DELIVERY  = 0x40      # /* Unable to deliver MPEG stream*/


    __toString = { 0x0 : "LSCP_OK",
                   0x10 : "LSCP_BAD_REQUEST",
                   0x11 : "LSCP_BAD_STREAM",
                   0x12 : "LSCP_WRONG_STATE",
                   0x13 : "LSCP_UNKNOWN",
                   0x14 : "LSCP_NO_PERMISSION",
                   0x15 : "LSCP_BAD_PARAM",
                   0x16 : "LSCP_NO_IMPLEMENT",
                   0x17 : "LSCP_NO_MEMORY",
                   0x18 : "LSCP_IMP_LIMIT",
                   0x19 : "LSCP_TRANSIENT",
                   0x1a : "LSCP_NO_RESOURCES",
                   0x20 : "LSCP_SERVER_ERROR",
                   0x21 : "LSCP_SERVER_FAILURE",
                   0x30 : "LSCP_BAD_SCALE",
                   0x31 : "LSCP_BAD_START",
                   0x32 : "LSCP_BAD_STOP",
                   0x40 : "LSCP_MPEG_DELIVERY"}
    @classmethod
    def tostring(cls, val):
        return cls.__toString.get(val)

    @classmethod
    def fromstring(cls, str):
        i = str.upper()
        for k,v in cls.__toString.iteritems():
            if v == i:
                return k
        return None



class LscpStateEnum:
    LSCP_INIT = -1
    LSCP_ALLOCATE_START = 0
    LSCP_TRANSLATE_URL = 1
    LSCP_ALLOCATE_END = 2
    LSCP_PLAY_SENT = 3
    LSCP_PLAY_RECEIVED = 4
    LSCP_PAUSE_SENT = 5
    LSCP_PAUSE_RECEIVED =6
    LSCP_RESUME_SENT = 7
    LSCP_RESUME_RECEIVED  = 8
    LSCP_STATUS_SENT = 9
    LSCP_STATUS_RECEIVED = 10

    LSCP_DONE_RECEIVED = 11
    LSCP_EOS_START = 12
    LSCP_EOS_END = 13



class LSCP_Op_code_enum(Enum):
    LSCP_PAUSE  = 0x1
    LSCP_RESUME = 0x2
    LSCP_STATUS = 0x3
    LSCP_RESET  = 0x4
    LSCP_JUMP   = 0x5
    LSCP_PLAY   = 0x6
    LSCP_DONE   = 0x40
    LSCP_PAUSE_REPLY  = 0x81
    LSCP_RESUME_REPLY = 0x82
    LSCP_STATUS_REPLY = 0x83
    LSCP_RESET_REPLY  = 0x84
    LSCP_JUMP_REPLY   = 0x85
    LSCP_PLAY_REPLY   = 0x86

    __toString = { 0x1 : "LSCP_PAUSE", 0x2 : "LSCP_RESUME", 0x3 : "LSCP_STATUS", 0x4 : "LSCP_RESET", 0x5 : "LSCP_JUMP", 0x6 : "LSCP_PLAY", 0x40 : "LSCP_DONE", 0x81 : "LSCP_PAUSE_REPLY"
        , 0x82 : "LSCP_RESUME_REPLY", 0x83 : "LSCP_STATUS_REPLY" , 0x84 : "LSCP_RESET_REPLY", 0x85 : "LSCP_JUMP_REPLY", 0x86 : "LSCP_PLAY_REPLY"}

    @classmethod
    def tostring(cls, val):
        return cls.__toString.get(val)

    @classmethod
    def fromstring(cls, str):
        i = str.upper()
        for k,v in cls.__toString.iteritems():
            if v == i:
                return k
        return None


class NTP_enum:
    NOW = 0x80000000
    END = 0x7fffffff


class LSCP_common_header(object):
    def __init__(self,header_data):
        try:
            Response = namedtuple('Response', 'version transaction_id op_code status_code stream_handle')
            parsed = Response._make(struct.unpack('!BBBBI', header_data[0:8]))
        except Exception, x:
            raise x

        #self.version = parsed.version
        #self.transaction_id  = parsed.transaction_id


        self.op_code_str =LSCP_Op_code_enum.tostring(parsed.op_code)
        self.status_code_str = LSCP_status_enum.tostring(parsed.status_code)
        self.op_code =parsed.op_code
        self.status_code = parsed.status_code
        #self.stream_handle = parsed.stream_handle

class LSCP_Response(LSCP_common_header):
    def __init__(self, data):

        LSCP_common_header.__init__(self, data)
        Response = namedtuple('Response', 'current_NPT scale_num scale_denom mode')
        parsed = Response._make(struct.unpack('!IhHB', data[8:17]))
        self.current_NPT = parsed.current_NPT
        self.scale = parsed.scale_num
        #self.scale_denom = parsed.scale_denom
        #self.mode = parsed.mode

    def __str__(self):
        msg = "{"
        for k,v in vars(self).iteritems():
            msg+=" " + k + ": " + str(v)

        return msg + "}"


class LSCP_Request(object):
    def __init__(self,stream_handle,start_ntp,end_ntp,op_code,scale,slow):
        self.stream_handle = stream_handle

        if(end_ntp == "END"):
            self.end_ntp = NTP_enum.END
        else:
            self.end_ntp = end_ntp

        self.op_code = op_code
        self.scale = scale
        self.slow = slow
        if(start_ntp == "NOW"):
            self.start_ntp = NTP_enum.NOW
        else:
            self.start_ntp = start_ntp

        if self.op_code == LSCP_Op_code_enum.LSCP_PLAY:
            if(self.scale>0):
                self.end_ntp = NTP_enum.END
            else:
                self.end_ntp = 0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        data = ""
        try:
            msg_header = struct.pack(">BBBBI",1,1,self.op_code,0,int(self.stream_handle))
            if self.op_code == LSCP_Op_code_enum.LSCP_PLAY:
                data = struct.pack("!IIhH",int(self.start_ntp),int(self.end_ntp),int(self.scale),int(self.slow))
            elif self.op_code == LSCP_Op_code_enum.LSCP_RESUME:
                data = struct.pack("!IhH",int(self.start_ntp),int(self.scale),int(self.slow))
            elif self.op_code == LSCP_Op_code_enum.LSCP_PAUSE:
                data = struct.pack("!I",int(NTP_enum.NOW))
            elif self.op_code == LSCP_Op_code_enum.LSCP_STATUS:
                data = ""
        except Exception,e:
            print e
        return  msg_header + data
