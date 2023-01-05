def coro():
    print ('before yield')
    a = yield 'the yield value'
    b = yield a
    print(f"done!")
c=coro()
    # this does not execute the generator, only creates it

     # If you use c.send('a value') here it could _not_ do anything with the value
     # so it raises an TypeError! Remember, the generator was not executed yet,
     # only created, it is like the execution is before the `print 'before yield'`

     # This line could be `c.send(None)` too, the `None` needs to be explicit with
     # the first use of `send()` to show that you know it is the first iteration
print (next(c)) # will print 'before yield' then 'the yield value' that was yield

print (c.send('first value sent')) # will print 'first value sent'
print (c.send('sec value sent')) # will print 'first value sent'