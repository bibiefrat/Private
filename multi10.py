import sys
import subprocess
import math

def isprime(n):
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False

    return True

def worker(start, end):
    count = 0
    for i in range(start, end):
        if isprime(i):
            count += 1

    print(count)


def master():
    p1 = subprocess.Popen([sys.executable, sys.argv[0], '1', '250000'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen([sys.executable, sys.argv[0], '250000', '500000'], stdout=subprocess.PIPE)
    p3 = subprocess.Popen([sys.executable, sys.argv[0], '500000', '750000'], stdout=subprocess.PIPE)
    p4 = subprocess.Popen([sys.executable, sys.argv[0], '750000', '1000000'], stdout=subprocess.PIPE)

    p1.wait()
    p2.wait()
    p3.wait()
    p4.wait()

    c1 = int(p1.stdout.read())
    c2 = int(p2.stdout.read())
    c3 = int(p3.stdout.read())
    c4 = int(p4.stdout.read())
    print(c1 + c2 + c3 + c4)

if len(sys.argv) == 1:
    master()
else:
    # worker(*[int(x) for x in sys.argv[1:]])
    worker(int(sys.argv[1]), int(sys.argv[2]))

