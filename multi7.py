#Data can be stored in a shared memory map using Value or Array. For example, the following code
#The 'd' and 'i' arguments used when creating num and arr are typecodes of the kind used by the array module: 'd' indicates a double precision float and 'i' indicates a signed integer. These shared objects will be process and thread-safe.

#For more flexibility in using shared memory one can use the multiprocessing.sharedctypes module which supports the creation of arbitrary ctypes objects allocated from shared memory.
from multiprocessing import Process, Value, Array

def f(n, a):
    n.value = 3.1415927
    for i in range(len(a)):
        a[i] = -a[i]

if __name__ == '__main__':
    num = Value('d', 0.0)
    arr = Array('i', range(10))

    p = Process(target=f, args=(num, arr))
    p.start()
    p.join()

    print num.value
    print arr[:]
