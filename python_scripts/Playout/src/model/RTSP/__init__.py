import re
import threading




def parse_massages(buffer,binary = False):
    return parse_rtsp_massages(buffer,binary)

def parse_rtsp_massages(buffer,binary = False):

    try:
        start = re.search(r"RTSP/1.0|ANNOUNCE",buffer)

        rtsp_txt =  buffer[start.start():buffer.rfind("\r\n")+2]

        msg_start =0
        msg_end = 0
        massages = []
        while(msg_end<len(rtsp_txt)):
            if(check_buffer_has_complete_massage(rtsp_txt[msg_end:])!=-1):
                msg_end+= check_buffer_has_complete_massage(rtsp_txt[msg_end:])[1]
                msg =  rtsp_txt[msg_start:msg_end]
    
                massages.append(RtspResponse(msg))
                msg_start =  msg_end
            else:
                break
        return  massages
    except Exception,x:
        
        print x,buffer
        raise x


def is_rtsp_response(buffer):
    return ("RTSP" in buffer or "ANNOUNCE" in buffer)


def check_buffer_has_complete_massage(buffer):
    # print "buffer starts with RTSP"
    if(str(buffer).find("ANNOUNCE")>=0):
        massage_start_index = str(buffer).find("ANNOUNCE")
    else:
        massage_start_index = str(buffer).find("RTSP/1.0")
    if(massage_start_index == -1):
    #            print "critical error : no rtsp massage found in buffer"
        return -1
    message_end_index = str(buffer).find("\r\n\r\n")+4
    if(message_end_index == -1):
        print "critical error - not a complete message w8ing for next buffer..."
        return -1
    else:
        if(str(buffer[massage_start_index:message_end_index]).find("Content-Length") != -1):
            content_length = int(re.search(r"Content-Length: (?P<length>.*?)\r\n",buffer).group(1))
            if(buffer[message_end_index :] >= content_length):
                #print "massage content found in buffer "+ str(content_length)
                return  massage_start_index,message_end_index  + content_length
            else:
                print "critical error - not all message content found in buffer"
                return -1
        else:
            return massage_start_index,message_end_index



class GlobalCseq(object):
    def __init__(self,start_cseq =0):
        self.Cseq = start_cseq
        self.session_cseq_lock = threading.Lock()
        self.session_cseq_dict = {}

    def GetNextCseq(self,session):
        try:
            self.session_cseq_lock.acquire()
            self.Cseq+=1
            self.session_cseq_dict[self.Cseq] = session
            return self.Cseq
        finally:
            self.session_cseq_lock.release()

    def GetSession(self,Cseq):
        try:
            self.session_cseq_lock.acquire()
            return self.session_cseq_dict.pop(Cseq)
        finally:
            self.session_cseq_lock.release()

    def GetCurrentCseq(self):
        return self.Cseq



class SessionStateEnum:
    INIT = -1
    DESCRIBE_SENT = 0
    DESCRIBE_RECEIVED = 1
    SETUP_SENT = 2
    SETUP_RECEIVED = 3
    PLAY_SENT = 4
    PLAY_RECEIVED = 5
    GET_PARAMETERS_SENT = 6
    GET_PARAMETERS_RECEIVED = 7
    TRICK_PLAY_SENT = 8
    TRICK_PLAY_RECEIVED = 9
    PAUSE_SENT = 10
    PAUSE_RECEIVED = 11
    TEARDOWN_SENT = 12
    TEARDOWN_RECEIVED = 13
    ANNOUNCE_RECEIVED = 14
    CLOSED = 15

class rtspVerbEnum:
    DESCRIBE = "DESCRIBE"
    SETUP = "SETUP"
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    TEARDOWN = "TEARDOWN"
    GETPARAMS = "GET_PARAMETER"

class RTSPStatusCodeEnum:
    CONTINUE = 100
    OK = 200
    CREATED = 201
    LOW_ON_STORAGE_SPACE  = 250
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    MOVED_TEMPORARILY = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIME_OUT = 408
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    REQUEST_ENTITY_TOO_LARGE = 413
    REQUEST_URI_TOO_LARGE = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    PARAMETER_NOT_UNDERSTOOD = 451
    CONFERENCE_NOT_FOUND = 452
    NOT_ENOUGH_BANDWIDTH = 453
    SESSION_NOT_FOUND = 454
    METHOD_NOT_VALID_IN_THIS_STATE = 455
    HEADER_FIELD_NOT_VALID_FOR_RESOURCE = 456
    INVALID_RANGE = 457
    PARAMETER_IS_READ_ONLY = 458
    AGGREGATE_OPERATION_NOT_ALLOWED =  459
    ONLY_AGGREGATE_OPERATION_ALLOWED = 460
    UNSUPPORTED_TRANSPORT = 461
    DESTINATION_UNREACHABLE = 462
    KEY_MANAGEMENT_FAILURE  = 463
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED =501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIME_OUT = 504
    RTSP_VERSION_NOT_SUPPORTED = 503
    OPTION_NOT_SUPPORTED = 551



class RtspResponse:
    code = 0
    description = ""
    headers = {}
    def __init__(self,code,description,headers):
        self.code = code
        self.description = description
        self.headers = headers
        self.sessionId = ""

    def __init__(self,msg):
        try:
#            print "RAW msg:",msg
            if("ANNOUNCE" in msg):
                print "********************ANNOUNCE************************"
                self.code = 200
                self.description = "ANNOUNCE"

            else:
                code_desc =re.search(r"RTSP/1.0 (?P<code>.*?)\s(?P<desc>.*?)\r\n",msg)
                self.code,self.description =  int(code_desc.group(1)),code_desc.group(2)
        

            hedrs = re.findall(r"(?P<name>.*?)[:\s+|=\s+](?P<value>.*?)\r\n", msg)
            for p in xrange(len(hedrs)):
                if(hedrs[p][1] == ""):
                    hedrs[p]= hedrs[p][0]," "

    
            self.headers = dict(hedrs)
#            for k,v in self.headers:
#                self.headers[k] = v.strip()

        except Exception,e:
            print e

    def getSessionId(self):
        if "Session" in self.headers:
            return self.headers["Session"]


    def __str__(self):

        if self.code !=200:
            resp="RTSP ERROR ->"
        else:
            resp="RTSP response ->"

        resp += " Code="+str(self.code) + " Description=\""+ self.description + "\"" + " " + str(self.headers)
        if "Session" in self.headers:
            resp += " Session=" +self.headers["Session"]
        if "CSeq" in self.headers:
            resp += " CSeq=" +self.headers["CSeq"]

        return resp
