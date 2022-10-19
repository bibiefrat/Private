import sys
import urllib2
import libxml2
from definitions import SessExceptions
import socket


class testing_component:
    def __init__(self, manager):
        self.manager = manager

    def manager_pars_response(self, response, xpath):
        #print "xpath-->%s" % (xpath)
        ans = response.xpathEval(xpath)
        #print ans[0].content
        return ans[0].content

    def test_component(self):
        # setting default timeout for manager session
        socket.setdefaulttimeout(60)

        urlManager = "http://%s/identity?X=0" % (self.manager)

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