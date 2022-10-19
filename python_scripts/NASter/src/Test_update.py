import md5
import os
import time
import sys
from FileHandler import FileHandler
from Globals import update_cfg
from Globals import NASter_cfg

#9bbcaf3f8a2d063cf716eefe1d72a0c5

if __name__ == '__main__':

    src = FileHandler(sys.argv[1],'rb')
    chksum = md5.new()

    update_cfg["update_size"] = long(update_cfg["update_size"])*1024
    update_cfg["update_position"] = long(update_cfg["update_position"])*1024

    update_pos_reached = False
    if(update_cfg["update_position"]<=int(NASter_cfg["md5_read_chunk_size"])):
        update_pos_reached = True
        buf = src.read(update_cfg["update_position"])
        chksum.update(buf)
    else:
        buf = src.read()


    checksum_updated = False
    while len(buf) > 0:
        if(update_pos_reached):
            print "reached position " + str(src.get_position())
            chksum.update('x'*update_cfg["update_size"])
            src.skip(update_cfg["update_size"])
            update_pos_reached = False
            checksum_updated = True
            buf = src.read()
        else:
            chksum.update(buf)
            if(src.get_position() + int(NASter_cfg["md5_read_chunk_size"]) >= update_cfg["update_position"] and checksum_updated == False):
                buf = src.read(update_cfg["update_position"] - src.get_position())
                update_pos_reached = True
                chksum.update(buf)
                continue

            buf = src.read()

    src.close()



    print chksum.hexdigest()


    src = FileHandler(sys.argv[1],'rb+')
    src.update()
    src.close()

    src = FileHandler(sys.argv[1],'rb')
    print src.get_md5()
    src.close()


    print os.system("md5sums.exe \"" + sys.argv[1] + "\"")