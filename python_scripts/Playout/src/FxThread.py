import threading
from time import ctime

class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def getResult(self):
        return self.res

    def run(self):
        print 'starting', self.name, 'at:', ctime(), '\n'
        self.res = apply(self.func, self.args)
        #self.res = self.func(*self.args)
        print self.name, 'finished at: ', ctime(), '\n'