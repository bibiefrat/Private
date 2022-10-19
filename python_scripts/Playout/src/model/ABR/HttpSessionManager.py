from StringIO import StringIO
import calendar

import time
from datetime import datetime

import httplib
#from definitions.Logger import timeit

from model.ABR import   httpparse

from model.SessionManager import _SessionManager




def utc_to_local(t):
    secs = calendar.timegm(t)
    return time.localtime(secs)


def date_try_parse(date,format):
    try:
        return datetime.strptime(date, format)
    except :
        return None


class _HttpSessionManager(_SessionManager):
    def __init__(self, networkService,sendingThread):
        super(_HttpSessionManager, self).__init__(networkService,sendingThread)
        self.session_files_dict = {}

    def handleSessionState(self, session):
        super(_HttpSessionManager, self).handleSessionState(session)


    def __handle_fragment_start__(self,session,fragment_headers,raw_data):
#        print self.session_files_dict.keys(),session.private_ID
        if(self.session_files_dict.has_key(session)):
            print "Error"
        else:
            session.session_log.debug("session " + str(session.private_ID) +" "+ str(fragment_headers.getheader("Content-Length")))
            self.session_files_dict[session] = (int(fragment_headers.getheader("Content-Length")),len(raw_data))

    def __handle_fragment_data__(self,session,raw_data):
        if(self.session_files_dict.has_key(session)):
            total_length,current_length = self.session_files_dict[session]
            current_length+=len(raw_data)
            if(current_length == total_length):
                self.handle_fragment_response(session)
                self.session_files_dict[session] = None
                self.session_files_dict.pop(session)
            elif(current_length<total_length):
                self.session_files_dict[session] = (total_length,current_length)
            else:
#                self.session_manager_log.error("content length for fragment is larger the total fragment length " + str(current_length) +"/" + str(total_length) + " " + str(session)
                session.session_log.error("content length for fragment is larger the total fragment length " + str(current_length) +"/" + str(total_length))
        else:
            print "Error"


    def handleReceived(self, session, msg):
        if(msg.startswith("HTTP")):
            response = httpparse(StringIO(msg))
            response_msg = response.read(len(msg[msg.index("\r\n\r\n"):]))
            if(response.length == 0):
                self.handleHttpMsg(session,response,response_msg)
                return
            elif( "video/MP2T" in response.getheader("Content-Type") or "video/mp4" in response.getheader("Content-Type")):
                self.__handle_fragment_start__(session,response,response_msg)

            else:
                response.length+=len(response_msg)
                session.TmpBuffer = (response,response_msg)
                return

        else:
            if(session.TmpBuffer!=None):
                response,response_msg = session.TmpBuffer
                response_msg += msg

                if(response.length == len(response_msg)):

                    self.handleHttpMsg(session,response,response_msg)
                    session.TmpBuffer = None
                else:
                    if(len(response_msg)>response.length):
                        self.session_manager_log.critical("should not be here!!!!!!!!!!!!!!!!!!!!11")
                    session.TmpBuffer = (response,response_msg)
                    return
            else:
                #this is for video chunks
                self.__handle_fragment_data__(session,msg)





    def handleHttpMsg(self, session, msg,content=None):

        session.state+=1

        if(msg.status != httplib.OK ):
            session.session_log.error(content)
            return

    def handle_fragment_response(self,session):
        print str(session.session_id) + " done fragment"















