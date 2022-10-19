'''
Created on Aug 6, 2012

@author: shy
'''
import ConfigParser
import urllib2
import libxml2

if __name__ == '__main__':
    #/X/regs/elem[contains(name,"Test_")]/id
    Config = ConfigParser.ConfigParser()
    Config.read("../conf/conf.ini")
    proxy = Config.get("General", "MP_ip")
    
    
    MP_ip_port = proxy+ ":" + str(5929)
    url = "http://%s/get_regions?X=0" %(MP_ip_port)
    all_managers_info = urllib2.urlopen(url).read()
    all_managers = libxml2.parseDoc(all_managers_info)
    
    managers_ids = all_managers.xpathEval("/X/regs/elem")

    for manager in managers_ids:
        manager_name = manager.xpathEval("name")[0].content
        if(str(manager_name).startswith("Test")):
            manager_id = manager.xpathEval("id")[0].content
            print " delete manager id="+str(manager_id)
            delete_url = "http://%s/remove_region?id=%s" %(MP_ip_port,manager_id)
            urllib2.urlopen(delete_url)
        
    all_managers.freeDoc()
    pass