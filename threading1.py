import threading
import math

class Counter:
    def __init__(self):
        self.val = 0
        self.lock = threading.Lock()

    def found_prime(self):
        self.lock.acquire()
        self.val += 1
        self.lock.release()

def isprime(n):
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False

    return True

def worker(counter, start, end):
    for i in range(start, end):
        if isprime(i):
            counter.found_prime()

c = Counter()

t1 = threading.Thread(target=worker, args=(c, 1, 250000))
t2 = threading.Thread(target=worker, args=(c, 250000, 500000))
t3 = threading.Thread(target=worker, args=(c, 500000, 750000))
t4 = threading.Thread(target=worker, args=(c, 750000, 1000000))

[t.start() for t in [t1, t2, t3, t4]]
[t.join() for t in [t1, t2, t3, t4]]

print(c.val)




