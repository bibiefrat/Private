import random
import sys
from FileHandler import FileHandler
from Globals import rw_cfg, NASter_cfg


if __name__ == '__main__':
    src = FileHandler(sys.argv[1],'rb+')
    dst = FileHandler(sys.argv[2],'rb+')
    chunk_size = int(NASter_cfg["fixed_chunks_size"])*1024
    file_size = src.size -chunk_size
    if(int(rw_cfg["read_first"]) == 1):
        dst.read_from_position(0,chunk_size)

    for i in xrange(int(rw_cfg["number_of_iterations"])):
        rnd_position = random.randint(0,file_size)
        dst.write("z"*chunk_size,rnd_position)
        data = src.read_from_position(rnd_position,chunk_size)
        if("z"*chunk_size not in data):
            print "ERROR no match at position: " +str(rnd_position)
#            print data



    src.close()
    dst.close()