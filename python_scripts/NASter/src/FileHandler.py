import md5
import os
import random
import sys
from Globals import NASter_cfg
from Globals import update_cfg

SYSTEM = sys.platform

class FileHandler(object):
    def __init__(self,filename,mode):
        self.mode = mode
        self.filename = filename
        if(SYSTEM == "win32" or NASter_cfg["use_o_direct"] == "False"):
            self.fd = open(filename,mode=self.mode)
        else:
            if("w" in self.mode or "r+" in self.mode):
                print "detected linux and write mode - using _O_DIRECT"
                tmp = os.open(filename,os.O_DIRECT|os.O_RDWR|os.O_CREAT)
                self.fd = os.fdopen(tmp, "w+",0)
            else:
                self.fd = open(filename,mode=self.mode)

        self.size = os.path.getsize(filename)
        self.chunks = []




    def init_chunks(self):
        if(not "w" in self.mode):
            if(int(NASter_cfg["fixed_chunks_size"]) >0):
                print "Fixed chunk size: " + NASter_cfg["fixed_chunks_size"]  + " KB"
                for i in xrange(0,self.size,1024*int(NASter_cfg["fixed_chunks_size"])):
                    #print "chunk at position " + str(i)  + " size " + str(1024*int(cfg["fixed_chunks_size"]))
                    if(self.size-i<int(NASter_cfg["fixed_chunks_size"])*1024):
                        #print "small chunk - " + str(self.size-i) + " break"
                        self.chunks.append((i,(self.size-i)))
                        break
                    self.chunks.append((i,int(1024*int(NASter_cfg["fixed_chunks_size"]))))
            else:
                print "Fixed chunk size: Min" + NASter_cfg["random_chunk_size_min"] + " KB Max " +  NASter_cfg["random_chunk_size_max"] + " KB"
                to_read = 0
                while(to_read<self.size):
                    if(self.size-to_read<int(NASter_cfg["random_chunk_size_min"])*1024):
                        self.chunks.append((to_read,(self.size-to_read)))
                        #print "small chunk - " + str(self.size-to_read) + " break"
                        break
                    chunk_size = self.get_random_chunk_size()*1024
                    self.chunks.append((to_read,chunk_size))
                    #print "chunk at position " + str(to_read)  + " size " + str(chunk_size)  + " left  "  + str(self.size-to_read)
                    to_read+=chunk_size


    def hashfile(self,blocksize = int(NASter_cfg["md5_read_chunk_size"])):
        self.skip(0)
        hasher = md5.new()
        buf = self.fd.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = self.fd.read(blocksize)
        return hasher.hexdigest()

    def truncate(self,newSize):
        self.fd.truncate(newSize)
        self.size =newSize

    def check_truncate(self,newSize):
        test_pass = True
        oldSize = self.size
        self.truncate(newSize)
        self.fd.seek(oldSize)
        seg = self.read()
        while(len(seg)>0):
            if(seg!=u"\u0000"*len(seg)):
                print "ERROR in position " + str(self.fd.tell()-int(NASter_cfg["md5_read_chunk_size"]))
                test_pass = False
            seg = self.read()


        print "Test pass: " + str(test_pass)

    def skip(self,size):

        self.fd.seek(self.fd.tell() + size)

    def get_position(self):
       return self.fd.tell()

    def get_md5(self):
        return self.hashfile()

    def get_random_chunk_size(self):
        return random.randint(int(NASter_cfg["random_chunk_size_min"]),int(NASter_cfg["random_chunk_size_max"]))

    def read_from_position(self,position,amount):
        self.fd.seek(position)
        return self.fd.read(amount)

    def read(self,blocksize = int(NASter_cfg["md5_read_chunk_size"])):
        return self.fd.read(blocksize)


    def update(self,position= long(update_cfg["update_position"])*1024,amount = long(update_cfg["update_size"])*1024):
        self.fd.seek(position)
        self.fd.write('x'*amount)


    def write(self,data,position):
        self.fd.seek(position)
        self.fd.write(data)

    def get_segment_count(self):
        return len(self.chunks)

    def get_random_segment(self):

        chunk = random.choice(self.chunks)
        self.chunks.remove(chunk)
        return (self.read_from_position(chunk[0],chunk[1]), chunk[0])





    def close(self):
        self.fd.flush()
        self.fd.close()

