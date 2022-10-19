'''
Created on Aug 12, 2014

This module provides an API to access a remote server that accepts and returns XML data using HTTP

Usage Example:
    1. create a new HTTPRequestFactory object:
        serviceFactory = HTTPRequestFactory('192.168.5.61', 5929)
    2. create functions that call services on the server:
        add_playout_profile = serviceFactory.makeServiceRequestFunc('add_playout_profiles', 'POST', 'requests/add_playout_profile', True,
                                                                    'application/atom+xml', 'add_playout_profile')
        add_channel = serviceFactory.makeServiceRequestFunc('multicast_channel/update', 'POST', 'requests/add_channel.xml',
                                                            True,'application/atom+xml', 'create_channel')
    3. change request parameters:
        add_playout_profile.setRequestBodyXMLValue('./profile/name', 'MyProfile')
                                                                 
    4. invoke the functions and get response objects:
        response1 = add_playout_profile()
        response2 = add_channel()
        
    5. get data out of reponses:
        status = int(response1.getHTTPStatus())
        profile_id = response1.getXMLvalue('./value/playout_profile/id')

@author: yuval
'''

import sys
import httplib2
from xml.etree import ElementTree

class HTTPRequestFactory(object):
    '''
    This class provides the ability to use a server's services using HTTP requests.
    Use makeServiceRequestFunc to create a function that communicates with the server.
    This function can also be changed before and after calls, and can be invoked as many times as needed.  
    '''
    
    def __init__(self, serverIPAddress, serverServicePort):
        '''
        Builds a new HTTPRequestFactory
        @param serverIPAddress: IP as string
        @param serverServicePort: port as int
        '''
        self._serverIPAddress = serverIPAddress
        self._serverServicePort = serverServicePort
        
    def makeServiceRequestFunc(self, servicePath, requestMethod = 'GET', requestBody = None, requestBodyFromFile = False,
                               requestMimeType = 'text/xml',functionName = ''):
        '''
        Returns a callable ServiceRequestFunc function.
        When the function is called, it sends a request to the server that was defined in the factory.
        After getting a response from the server, the function returns two strings: 
        the first one is the HTTP status response, and the second one is the response body.
        @param servicePath: the relative URL of the service in the server. Any URL parameters should also be added here. 
        @param requestMethod: a string: GET, POST, DELETE, PUT etc... Default: 'GET'
        @param requestMimeType: The MIME type of the request. A corresponding header will be added. Default: 'text/xml'
        @param requestBody: A string to be sent as the request's body. If requestBodyFromFile is True, then the string should be a path
                            to a file. The content of the request's body will be taken from that file. Default: None
        @param requestBodyFromFile: If True, then requestBody will be treated as a path to a file. Default: False
        @param functionName: Optional. This name will be used to identify the function printouts to the console (exceptions, assertions etc...) 
        '''
        return self.ServiceRequestFunc(self._serverIPAddress,self._serverServicePort,servicePath,requestMethod,requestBody,requestBodyFromFile
                                       ,requestMimeType,functionName)
        
        
        
    class ServiceRequestFunc(object):
        '''
        This class represents a function that sends a request to the server
        '''
        
        def __init__(self,serverIPAddress,serverServicePort,servicePath,requestMethod,requestBody,requestBodyFromFile,
                     requestMimeType,functionName):
            self._serverIPAddress = serverIPAddress
            self._serverServicePort = serverServicePort
            self._servicePath = servicePath
            self._requestMethod = requestMethod.upper()
            self._requestMimeType = requestMimeType
            self._requestBodyFromFile = requestBodyFromFile
            self._headers = {}
            self._functionName = functionName 
            
            if self._requestBodyFromFile:
                with open(requestBody) as bodyFile:
                    self._requestBody = bodyFile.read()
            else:
                self._requestBody = requestBody
            
        def __call__(self, print_request=True, print_responset=True):
            '''
            Send the request to the server.
            To invoke this, simply invoke the function you got from the factory.
            @return: A tupple: the first element is the HTTP response status line (status code and headers), and the second element is the response body 
            '''
            response, content = '',''
            try:
                #Prepare request headers and body
                
                # close the connection by default (httpClient object is not saved anyway, so the connection will be forgotten on the client side)
                if not self._headers.get('Connection'):
                    self._headers['Connection']= 'close'
                self._headers['Content-Type']= self._requestMimeType
                
                #Send request
                #TODO: log request and response    
                httpClient = httplib2.Http()
                if print_request:
                    print '\n' + str(self) + ': sending HTTP request:' + self._HTTP_request_string()
                response = httpClient.request('http://' + self._serverIPAddress + ':' + str(self._serverServicePort) + '/' + self._servicePath, 
                                                       self._requestMethod, self._requestBody, self._headers)
                responseObj = HTTPServiceResponse(response)
                if print_responset:
                    print '\n' + str(self) + ': received HTTP response:\n' + str(responseObj)
                return responseObj
            
            except Exception as e:
                #TODO: print exception to log file 
                raise AssertionError, 'Exception in ' + str(self) + ': ' + str(e), sys.exc_info()[2]
            
            
        
        def __str__(self):
            return 'ServiceRequestFunc - ' + self._functionName if self._functionName else 'ServiceRequestFunc'
               
        def _HTTP_request_string(self):
            returnStr = '\n' + self._requestMethod + ' http://' + self._serverIPAddress + ':' + str(self._serverServicePort) + '/' + self._servicePath
            for header_name,header_value in self._headers.iteritems():
                returnStr = returnStr + '\n' + header_name + ':' + header_value
            returnStr = returnStr + '\n' + (self._requestBody if self._requestBody else '')
            return returnStr
        
        
        
        def setServicePath(self, servicePath):
            self._servicePath = servicePath
        
        def setRequestMimeType(self,requestMimeType):
            self._requestMimeType = requestMimeType
           
        def setRequestMethod(self,requestMethod):
            self._requestMethod = requestMethod.upper()
            
        def addHeader(self,headerName,headerContent):
            self._headers[headerName]=headerContent
            
        def removeHeader(self,headerName):
            self._headers.pop(headerName,'headerNotInRequest')

        def setRequestBodyXMLValue(self,XPath,value):
            '''
            Will set the value of the first element that matches the XPath
            @param XPath: a string that represents the path to the desired element in the request's body XML
            @param value: the new value of the element
            '''
            try:
                xmlTree = ElementTree.fromstring(self._requestBody)
                element = xmlTree.find(XPath)
                element.text = value
                self._requestBody = ElementTree.tostring(xmlTree)
            except Exception as e:
                #TODO: log e
                raise AssertionError, 'Exception in ' + str(self) + ': ' + str(e), sys.exc_info()[2]
                
        def setRequestBodyXMLProperty(self,XPath,propertyName,value):
            '''
            @param XPath: a string that represents the path to the desired element in the request's body XML
            @param propertyName: the name of element's property to be changed
            @param value: the new value of the property
            '''
            try:
                xmlTree = ElementTree.fromstring(self._requestBody)
                element = xmlTree.find(XPath)
                element.set(propertyName,value)
                self._requestBody = ElementTree.tostring(xmlTree)
            except Exception as e:
                #TODO: log e
                raise AssertionError, 'Exception in ' + str(self) + ': ' + str(e), sys.exc_info()[2]
        
        def setRequestBodyXMLALLValues(self,XPath,value):
            '''
            Will set the value of all elements that match the XPath
            @param XPath: a string that represents the path to all the desired elements in the request's body XML
            @param value: the new value of the elements
            '''
            try:
                xmlTree = ElementTree.fromstring(self._requestBody)
                for elem in xmlTree.findall(XPath):
                    elem.text = value
                self._requestBody = ElementTree.tostring(xmlTree)
            except Exception as e:
                #TODO: log e
                raise AssertionError, 'Exception in ' + str(self) + ': ' + str(e), sys.exc_info()[2]
        
        

class HTTPServiceResponse(object):
    '''
    This class handles the responses returned by the ServiceRequestFunc functions that are created using HTTPRequestFactory
    '''
    
    def __init__(self,response):
        '''
        @param response: The response as received from the httplib2 server
        '''
        self._response = response
    
    def __str__(self):
        return  str(self._response[0]) + '\n' + str(self._response[1])
    
    
    def getXMLvalue(self,XPath):
        '''
        Returns the value of the first element in the XML tree that matches XPath
        @param XPath: XPath that matches the desired element
        '''
        try:
            return ElementTree.fromstring(self._response[1]).find(XPath).text
        except Exception as e:
            #TODO: log e
            raise
    
    def getXMLAllValues(self,XPath):
        '''
        Returns a list of values of all elements that match XPath.
        @param XPath: XPath that matches all the desired elements
        '''
        values=[]
        try:
            for elem in ElementTree.fromstring(self._response[1]).findall(XPath):
                values.append(elem.text)
            return values
        except Exception as e:
            #TODO: log e
            raise
    
    def getXMLtree(self):
        '''
        This enables the user to perform more complex evaluations on the XML response he got
        '''
        return ElementTree.fromstring(self._response[1]) 
        
    def getHTTPStatus(self):
        return self._response[0]['status']
    
    
    
    
    
    
    
    
    
    
    
    
    