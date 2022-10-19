def memoize(f):    
    def wrapped(n):
        try:
            return wrapped.dict[n]            
        except AttributeError:
            wrapped.dict = {}
            wrapped.dict[n]=f(n)
            return wrapped.dict[n]
        except KeyError:
            wrapped.dict[n]=f(n)
            return wrapped.dict[n]
        #return f(n)

    return wrapped

@memoize
def fib(n):
    print "fib(%d)" % n
    if n <= 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

print(fib(10))