'''
Created on Aug 5, 2012

@author: shy
'''



import BaseHTTPServer
import SimpleHTTPServer

import threading

import time
import socket
import httplib, urllib
import libxml2
import urllib2
from xml.dom.minidom import Document
import sys
import os.path


class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>Title goes here.</title></head>")
        self.wfile.write("<body><p>This is a test.</p>")
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then self.path equals "/foo/bar/".
        self.wfile.write("<p>You accessed path: %self</p>" % self.path)
        self.wfile.write("</body></html>")
    def do_POST(self):

        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length)
        
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if(self.path == "/proxy/get_boxes"):
            boxes = file("../boxes/"+str(self.server.server_port)+".xml").read()
            #print "sending box list\n" + boxes
            self.wfile.write(boxes)
            
        print "data = " + post_data
        
       
        

        
#       
#        self.wfile.write("<html><head><title>Title goes here.</title></head>")
#        self.wfile.write("<body><p>This is a test.</p>")
#        # If someone went to "http://something.somewhere.net/foo/bar/",
#        # then self.path equals "/foo/bar/".
#        self.wfile.write("<p>You accessed path: %self</p>" % self.path)
#        self.wfile.write("</body></html>")

class Manager(threading.Thread):


    def __init__(self,manager_ip,manager_port,manager_ID,MP_host,MP_port,numberOfBoxes,service_group):
        threading.Thread.__init__(self)
        self.manager_ip = manager_ip
        self.manager_port = manager_port
        self.manager_ID = manager_ID
        self.MP_host = MP_host
        self.MP_port = MP_port
        self.responses = {}
        self.service_group = service_group
        xml = self.CreateStatusXML(manager_port)
        self.keep_connection = httplib.HTTPConnection(self.MP_host,self.MP_port)
        
#        xml = file("../conf/get_regions.xml").read()
#        
#        regions = libxml2.parseDoc(xml)
#        regions.xpathEval("//X/regs/elem/id")[0].setContent(str(self.manager_ID))
#        regions.xpathEval("//X/regs/elem/name")[0].setContent("Test_"+str(manager_port))
#        regions.xpathEval("//X/regs/elem/manager_addr")[0].setContent(self.manager_ip + ":" + str(self.manager_port))
#        self.regions_response = str(regions)
#        regions.freeDoc()
#        
#        self.topology_get_warnings = file("../conf/topology_get_warnings.xml").read()
#        
#        self.responses["/topology_get_warnings"] = self.topology_get_warnings
#        self.responses["/get_regions"] = self.regions_response
        print "generating boxes"
        
        self.CreateBoxesXML(numberOfBoxes)
        
        
        print "Adding region to MP "
        manager_ip_port = self.manager_ip + "%3A" + str(self.manager_port)
        MP_ip_port = self.MP_host + ":" + str(self.MP_port)
        url = "http://%s/add_region?id=%s&address=%s&name=%s&type=0" % (
        MP_ip_port,self.manager_ID,manager_ip_port,"Test_"+str(manager_port))
        all_asset_info = urllib2.urlopen(url)
        
        
        print "manager init on ip:port - " + manager_ip + ":" + str(manager_port)
        
        
    def appendChild(self,doc,node,elem_name,elem_value):
        tmpnode =   node.appendChild(doc.createElement(elem_name)) 
        tmpnode.appendChild(doc.createTextNode(str(elem_value))) 
        

    def run(self):
        PORT_NUMBER = int(self.manager_port)
        HOST_NAME = str(self.manager_ip)
        server_class = BaseHTTPServer.HTTPServer
        #handler = MyHandler
        #handler.responses = self.responses
        httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
        
        print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
        try:
                httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
        
    def CreateBoxesXML(self, numberOfBoxes):

        if(os.path.exists("../boxes/" + str(self.manager_port) + ".xml")):
            return
        
        doc = Document()
        node = doc.createElement('X')
        boxes = node.appendChild(doc.createElement("boxes"))
        size = boxes.appendChild(doc.createElement("size"))
        size.appendChild(doc.createTextNode(str(numberOfBoxes)))
        for i in xrange(numberOfBoxes):
            elem = boxes.appendChild(doc.createElement("elem"))
            elem.setAttribute("id", str(i))
            self.appendChild(doc, elem, "id", str(self.manager_port) + "_" + str(i))
            self.appendChild(doc, elem, "size", "81920000000")
            self.appendChild(doc, elem, "concurrent_recordings", 0)
            self.appendChild(doc, elem, "delete_policy", 3)
            self.appendChild(doc, elem, "external_id", str(self.manager_port) + "_" + str(i))
            self.appendChild(doc, elem, "service_group_id", "%012X"%(int(self.service_group)))
            self.appendChild(doc, elem, "time_provisioned", time.time())
            self.appendChild(doc, elem, "available_space", "81920000000")

        doc.appendChild(node)
        xml_boxes_file = file("../boxes/" + str(self.manager_port) + ".xml", "w")
        xml_boxes_file.write(doc.toxml())


    def CreateStatusXML(self, manager_port):
        xml = file("../conf/status.xml").read()
        status = libxml2.parseDoc(xml)
        status.xpathEval("//X/address")[0].setContent(self.manager_ip + ":" + str(self.manager_port))
        status.xpathEval("//X/region_id")[0].setContent(str(self.manager_ID))
        status.xpathEval("//X/region_name")[0].setContent("Test_" + str(manager_port))
        status.xpathEval("//X/service_group_datas/elem/first")[0].setContent("%012X"%(int(self.service_group)))
        status.xpathEval("//X/service_group_datas/elem/second/ad_zone")[0].setContent("ad-zone"+str(self.service_group))
        self.status_xml = str(status)
       
        status.freeDoc()
        
        return xml
        

    def send_keep_alive(self):
      #  print "sending keep alive"
        #sock = socket.create_connection(("192.168.6.6",5929),10,(self.manager_ip,0))
        headers = {"Content-type": "text/xml","Accept": "*/*","Accept-Encoding": "gzip","Host": self.manager_ip,"Connection": "keep-alive"}
        try:
            self.keep_connection.request("POST", "/manager/new_state",self.status_xml,headers)
            #time.sleep(1)
            r1 = self.keep_connection.getresponse()
            r1.read(None)
            if(r1.status != 200):
                print r1.status, r1.reason
        except:
            self.keep_connection.close()
            self.keep_connection.connect()





