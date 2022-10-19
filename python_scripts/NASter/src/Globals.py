import sys; print('Python %s on %s' % (sys.version, sys.platform))
import ConfigParser

class AttributeDict(dict):
    def __getattr__(self, name):
        return self[name]


config = ConfigParser.ConfigParser()
path = "../"
cfgPath = "%s%s" % (path, "/conf/config.ini")
config.read(cfgPath)
NASter_cfg = AttributeDict(dict(config.items("NASter_cfg")))

update_cfg = AttributeDict(dict(config.items("update_cfg")))

truncate_cfg = AttributeDict(dict(config.items("truncate_cfg")))

rw_cfg = AttributeDict(dict(config.items("rw_cfg")))

hole_cfg = AttributeDict(dict(config.items("hole_cfg")))

