import time
import sys
from FileHandler import FileHandler


if __name__ == '__main__':

    src = FileHandler(sys.argv[1],'rb')
    dst = FileHandler(sys.argv[2],"wb+")

    src.init_chunks()

    start = time.time()
    while(src.get_segment_count()>0):
        seg,position = src.get_random_segment()
        dst.write(seg,position)

    dst.close()
    src.close()
    total_time = time.time() - start
    print "Time: " + str(total_time)  + " seconds"

    mbs = (src.size/(1<<20))/total_time

    print "Rate: " +  str(mbs) + " MB/s"
    src_md5 =  src.get_md5()
    dst_md5 =  dst.get_md5()

    print "src md5 " + src.get_md5()
    print "dst md5 " + dst.get_md5()

    if(src_md5 == dst_md5):
        print "Test: Pass"
    else:
        print "Test: Fail"

