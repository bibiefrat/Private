import ConfigParser
import cmd
import sys
import urllib2
import libxml2
import Pycmd

disks=[]


class atdict(dict):
    __getattr__= dict.__getitem__
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

def ini_parse():
    path = "../"
    print "reading configuration file"

    def ConfigSectionMap(section):
        try:
            options = atdict(config.items(section))
            for k,v in options.items():
                if(v.isdigit()):
                    options[k] = int(v)

        except ConfigParser.NoSectionError:
            print "Configuration file not found at "
            sys.exit(0)
        return options

    config = ConfigParser.ConfigParser()
    cfgPath = "%s%s" % (path, "/conf/config.ini")
    config.read(cfgPath)
    dict = ConfigSectionMap("Configuration")
    dict["cluster_manager_ip"] = dict["cluster_manager"].split(":")[0]
    print dict

    return dict

ini = ini_parse()

def node_content(node,xpath):
    return node.xpathEval(xpath)[0].content

def storage_id():
    storage_address = urllib2.quote("Address:Port")
    topology_url = "http://%s/FX_CM_Service/FX_Get_DB_Storage?storage_address=%s" % (
    ini.cluster_manager ,storage_address)
    topology_result = urllib2.urlopen(topology_url)
    xml_topology = topology_result.read()
    parse_storage = libxml2.parseDoc(xml_topology)
    p = dict()
    storage_vecs = parse_storage.xpathEval("//X/storage_vec/elem")
    for storage in storage_vecs:
        machine =  node_content(storage,"storage_mng_addrs/name")
#        port =  node_content(storage,"storage_mng_addrs/port")
        disk_id = node_content(storage,"storage_id")
        p[disk_id] =machine

        print disk_id + " = " +p[disk_id]

    parse_storage.freeDoc()

    return p



machines = storage_id()


commander = Pycmd.CmdControl("PermuTest", machines, ini.segment_size)
commander.cmdloop()