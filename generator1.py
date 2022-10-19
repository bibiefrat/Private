def my_enumerate(iterator):
    i = 0
    for val in iterator:
        yield i, val
        i += 1


def fib():
    x, y = 1, 1
    while True:
        x, y = y, x + y
        yield x

def gen():
    yield 10
    yield 20
    yield 30
    yield 40

for val in fib():
    print(val)
    if val > 200:
        break

s = 0
for idx, val in my_enumerate(fib()):
    if idx >= 10:
        break
    s += val
print(s)



