import exceptions

class MisconfigurationError(exceptions.Exception):
    def __init__(self, *args, **kwargs):
#        super(MisconfigurationError, self).__init__(*args, **kwargs)
        exceptions.Exception.__init__(self,*args, **kwargs)

class Manager_Err(exceptions.Exception):
    #color_loc = TerminalController()
    def __init__(self, reason, url):
        #Exeption.__init__()
        self.reason = reason
        self.url = url

        return

    def __str__(self):
        return "!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!\n" +\
               "\t\t\t\tRequest: " + str(self.url) + "\n" +\
               "\t\t\t\tRequest failed because : " + str(self.reason) + "\n" +\
               "\t\t\t    !*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!"


class SessAllocate_Err(exceptions.Exception):
    def __init__(self, numSess, reason, url):
        #Exeption.__init__()
        self.numSess = numSess
        self.reason = reason
        self.url = url

        return

class SessCreate_Err(exceptions.Exception):
    def __init__(self,  reason):
        exceptions.Exception.__init__(self,reason)
        self.reason = reason

        return


class RTSP_Command_Err(Exception):
    def __init__(self, msg,session = None,sessionId = None,Cseq=-1):
        Exception.__init__(self,msg)
        self.sessionId = sessionId
        self.Cseq = Cseq
        self.Session = session

        return

class Trick_Play_Err(exceptions.Exception):
    def __init__(self, numSess, reason, url):
        #Exeption.__init__()
        self.numSess = numSess
        self.reason = reason
        self.url = url

        return



    def __str__(self):
        return "!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!\n" +\
               "\t\t\t\t\tTrickplay in session " + str(self.numSess) + " has failed\n" +\
               "\t\t\t\t\tSent URL : " + str(self.url) + "\n" +\
               "\t\t\t\t\tOpening URL has failed because : " + str(self.reason) + "\n" +\
               "\t\t\t\t\t!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!"


class xml_parse_err(exceptions.Exception):
    def __init__(self, asset, url, reason):
        self.asset = asset
        self.reason = reason
        self.url = url

    def __str__(self):
        return "!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!\n" +\
               "\t\t\t\t\tXML parsing of : " + str(self.asset) + " has failed\n" +\
               "\t\t\t\t\tSent URL : " + str(self.url) + "\n" +\
               "\t\t\t\t\tReason : " + str(self.reason) + "\n" +\
               "\t\t\t\t\t!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!"


class tear_down__err(exceptions.Exception):
    def __init__(self, session_id, reason):
        self.session_id = session_id
        self.reason = reason

    def __str__(self):
        return "!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!\n" +\
               "\t\t\t\t\Session ID  " + str(self.session_id) + "\n" +\
               "\t\t\t\t\tReason : " + str(self.reason) + "\n" +\
               "\t\t\t\t\t!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!*!"

