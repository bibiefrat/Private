import random
import sys
import time
from FileHandler import FileHandler
from Globals import rw_cfg, NASter_cfg, hole_cfg


if __name__ == '__main__':
    src = FileHandler(sys.argv[1],'rb')
    dst = FileHandler(sys.argv[2],"wb+")
    if(int(NASter_cfg["fixed_chunks_size"]) <=0):
        print "only fixed sized chunk is supported"
        exit(1)

    src.init_chunks()
    chunk_size = int(NASter_cfg["fixed_chunks_size"])*1024
    del src.chunks[int(hole_cfg["hole_position"]):int(hole_cfg["hole_position"]) + int(hole_cfg["hole_size"])]

    print "dst file will have a hole at: " + str(int(hole_cfg["hole_position"])*chunk_size),
    print " hole size will be: " + str(int(hole_cfg["hole_size"]) * chunk_size)

    print "if on linux use command \"hexdump "+sys.argv[2]+" -s " + str(int(hole_cfg["hole_position"])*chunk_size) + " -n " +str(int(hole_cfg["hole_size"]) * chunk_size) + "\" to verify zeros"

    while(src.get_segment_count()>0):
        seg,position = src.get_random_segment()
        dst.write(seg,position)


    dst.close()
    src.close()

    src = FileHandler(sys.argv[1],'rb')
    dst = FileHandler(sys.argv[2],"rb")

    src_md5 =  src.get_md5()
    dst_md5 =  dst.get_md5()

    print "src md5 " + src_md5
    print "dst md5 " + dst_md5

    if(src_md5 == dst_md5):
        print "Test: Pass"
    else:
        print "Test: Fail"



