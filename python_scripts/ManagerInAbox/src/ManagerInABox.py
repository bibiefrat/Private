'''
Created on Aug 5, 2012

@author: shy
'''


from Manager import Manager
import time
import ConfigParser
import socket

#py_compile.compile("ManagerInABox.py")
def get_local_ip_address(target):
    ipaddr = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((target, 8000))
        ipaddr = s.getsockname()[0]
        s.close()   
    except:
        pass
    return ipaddr 


if __name__ == '__main__':
    Config = ConfigParser.ConfigParser()
    Config.read("../conf/conf.ini")
    start_port = Config.getint("General", "start_port")
    number_of_servers = Config.getint("General", "number_of_servers")
    number_of_boxes_per_server = Config.getint("General", "number_of_boxes_per_server")
    
    proxy = Config.get("General", "MP_ip")
    items = Config.items("General")
    service_groups = Config.get("General", "service_groups").split(",")
    
    Managers = []
    
    local_ip = get_local_ip_address(proxy)
    service_group_index = 0
    for i in xrange(number_of_servers):
        manager = Manager(local_ip,start_port+i,start_port+i,proxy,5929,number_of_boxes_per_server,
                          service_groups[service_group_index])
        service_group_index+=1
        if(service_group_index>=len(service_groups)):
            service_group_index = 0
        Managers.append(manager)
        manager.start()
        

    while(1):
        time.sleep(5)
        for manager in Managers:
            try:
                manager.send_keep_alive()
            except:
                pass
        
    pass