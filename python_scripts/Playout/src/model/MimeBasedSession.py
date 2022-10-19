from model.Session import Session

class MimeBasedSession(Session):
    def __init__(self, assets, stb_addr, streamer_id, numSess, sendingThread, scheduler):
        super(MimeBasedSession, self).__init__(assets, stb_addr, streamer_id, numSess, sendingThread, scheduler)
        self.headers = {}

    def BuildRequest(self,url,headers,content):
        buffer = url + "\r\n"
        for header in headers:
            if(header == "Content-Length" and content!=None):
                buffer+= header + ": " + str(len(content)) + "\r\n"

            else:
                if header in  self.headers :
                    buffer+= header + ": " + self.headers[header] + "\r\n"
                else:
                    print "Error composing " + url + " command header " + header +" is not in the session dictionary"

        buffer += "\r\n"
        if(content!=None):
            buffer+=content
        return buffer
