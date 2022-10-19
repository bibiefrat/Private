import sys
import math
import multiprocessing

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
    p1 = multiprocessing.Process(target=worker, args=(1, 250000))
    p2 = multiprocessing.Process(target=worker, args=(250000, 500000))
    p3 = multiprocessing.Process(target=worker, args=(500000, 750000))
    p4 = multiprocessing.Process(target=worker, args=(750000, 1000000))

    p1.start()
    p2.start()
    p3.start()
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        master()
    else:
        # worker(*[int(x) for x in sys.argv[1:]])
        worker(int(sys.argv[1]), int(sys.argv[2]))

