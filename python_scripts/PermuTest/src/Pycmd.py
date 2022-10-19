import cmd

import os
import signal


import pprint
def count_unique(seq):
    # not order preserving
    set = {}
    map(set.__setitem__, seq, [])
    return len(set.keys())



def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class CmdControl(cmd.Cmd):
    """Simple command processor example."""


    prompt = '> '




    def __init__(self,name,machines,segment_size):
        cmd.Cmd.__init__(self)
        print 'Welcome to the '+name+' script.   Type help or ? for list of commands.\n'
        self.machines = machines
        self.segment_size = segment_size
        signal.signal(signal.SIGTERM, self.handler)

    def do_shell(self, s):
        os.system(s)

    def help_shell(self):
        print "execute shell commands"





    def emptyline(self):
        pass


    def do_test(self, permutation):
        "Add number of sessions"
        if(permutation):

            print "ok - testing " + permutation
            segments = list(chunks(permutation.split(" "),self.segment_size))
            pprint.pprint(segments)
            machine_protected = True
            for segment in segments:
                tmp_m = []
                for disk in segment:
                    tmp_m.append(self.machines[str(int(disk)+1)])
                if(count_unique(tmp_m)!=self.segment_size):
                    print "NOT machine protected !!!"
                    print segment
                    machine_protected = False
                    break
                print tmp_m
            if(machine_protected):

                print " OK "

            unique =  count_unique(permutation.split(" "))
            print "unique " + str(unique)
        else:
            print "please provide permutation"



    def do_setSegmentSize(self,size):
        self.segment_size = int(size)


    def handler(self, signum, frame):
    # self.emptyline() does not work here
    # return cmd.Cmd.emptyline(self) does not work here

        self.do_EOF(1)
        return True

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    CmdControl(None).cmdloop()